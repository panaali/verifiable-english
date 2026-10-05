import VE.Norms.Admission
import VE.Norms.Flagged
import VE.Norms.Plain
import VE.Route.Run

/-! The `ve_norms_route` executable (docs/spec/norms.md 11.4), invoked as
`lean/.lake/build/bin/ve_norms_route <cases.json|->`. Each case is
`{"id", "environment", "kind", ...}`.

* `norms-elaborate`: `norms` (an array of norm objects, 3.2) → the regenerated
  layer order, Background (with generators), labelled layer premises
  (`layer:norms:<p>`), conflict targets (`p` and `r->m`, with argument sorts)
  and the fragment flag; or the shared diagnostic of `validate`.
* `norms-conflict`: `norms` and `packages` (target → Python's conflict package)
  → `verdict` `CONFLICT-FREE` when every target's certificate is bound and
  accepted (over the regenerated `E_base` and `Background_base` for a document
  with neither flags nor definitions, otherwise over Python's base environment
  and base Background), else `UNKNOWN` with the first failing target
  (`Flagged.replayConflict`). CONFLICT-FREE means the spec's `ConflictFree` on
  every base-admissible structure satisfying the flag premises
  (`Flagged.norms_flagged_conflict_sound`, `FlaggedSpec.norms_flagged_conflict_free`,
  and at this entry `FlaggedSpec.norms_wire_conflict_free`).
* `norms-conflict` with `witness` (`target`, base `model`, `tuple` of entity ids
  in argument order) → `verdict` `CONFLICT` when the regenerated target formula
  is true at the typed tuple of the validated base model (flags included), else
  `UNKNOWN` (`Flagged.norms_flagged_witness_sound`,
  `FlaggedSpec.norms_wire_conflict_refuted`).
* `norms-certificate`: `norms`, `premises`, `conclusion`, `certificate` →
  `valid`; the certificate binds the complete environment, the regenerated
  `flags ++ Background ++ layer premises` followed by `premises`, and the
  conclusion (`Flagged.norms_flagged_acceptance`).
* The three `norms-*` kinds accept `data@0` flags and W3 definitions; flag
  premises are regenerated and come first in Background (`Flagged`). The
  `Replay.replayConflict`, `replayWitness` and `replayEntailment` functions
  are not called here.
* `admission`: a W2 FOL `document` containing norm units → a checked report,
  source-bound report id and unit kinds; the answer is exactly
  `encodeAdmitted` of the checked admission (`Run.norms_wire_acceptance`).
* `background`, `evaluate` and `countermodel` on an environment with
  `regulated` declarations and no norm objects → `Plain.run`: the route's
  answer over the environment without the validated extension, with the
  profile premises added to Background and required of models.
* Any case without a norm construct (no `regulated` field, no `norms`, not a
  `norms-*` kind) is delegated unchanged to P0 `Route.Run.runCase`. A norm
  input never falls back to P0 after a failed decode.

W2 documents containing norm units use regenerated layer leaves and the
unchanged W2 graph checker. -/
namespace VE.Norms.Run
open Lean

/-- The executable dispatch test: a norm construct (a `regulated` declaration
or norm content) or a norms case kind. The `norms@0` profile alone is not a
construct; such P0 inputs delegate unchanged. -/
def usesNormsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let regulated := match (env.getObjValD "vocabulary").getObjValD "predicates" with
    | .obj kvs => kvs.toList.any (fun (_, e) => (e.getObjVal? "regulated").toBool)
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "norms-"
    | _ => false
  let normUnit := match (j.getObjValD "document").getObjValD "units" with
    | .arr units => units.toList.any (fun u => ((u.getObjValD "content").getObjVal? "norm").toBool)
    | _ => false
  regulated || (j.getObjVal? "norms").toBool || kind || normUnit

def reportJson (r : VE.Graph.Report) : Json :=
  Json.mkObj [("root", VE.Route.Run.claimJson r.root),
    ("assumptions", Json.arr (r.assumptions.map VE.Route.Run.claimJson).toArray)]

/-- P0's unchanged report identity domain (3.9). -/
def reportDomain (profiles : List String) : String :=
  s!"ve-report-{VE.Route.Wire.identityVersion profiles}\n"

/-- The report identity payload, over the complete validated source document
(not a formula projection). -/
def reportPayload (envId : String) (document : Json) (r : VE.Graph.Report) : Json :=
  Json.mkObj [("environment_id", .str envId), ("document", document), ("report", reportJson r)]

/-- The answer for an admitted document. -/
def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray)]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let envId ← VE.Route.Wire.environmentId res.src.ne.profiles res.canonical
  let reportId ← VE.CertificateWire.digest (reportDomain res.src.ne.profiles)
    (reportPayload envId document res.report)
  return encodeAdmitted id reportId res

/-- Every binding is the recomputed one (11.4 step 4): certificates name the
canonical source environment and their source ASTs, and the report id is the
digest of the canonical environment id, the complete source document and the
checked report. Equality of digests, not injectivity of SHA-256. -/
def BindingsMatchSourceAndRegeneration (environment document : Json) (res : Admission.Admitted)
    (reportId : String) : Prop :=
  Admission.CertificatesBound environment res ∧
  ∃ envId, VE.Route.Wire.environmentId res.src.ne.profiles res.canonical = .ok envId ∧
    VE.CertificateWire.digest (reportDomain res.src.ne.profiles)
      (reportPayload envId document res.report) = .ok reportId

/-- The 11.4 admission obligation for one answer: the raw input decodes to a
well-formed norm source, the answer is exactly the encoding of the checked
admission, every binding is recomputed from source and regeneration, the
report is admitted, and it is a semantic consequence of the regenerated
Background and layer premises and its remaining assumptions. -/
def AdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormed res.src.D = true ∧
    answer = encodeAdmitted id reportId res ∧
    Admission.SourceDecoded environment document res ∧
    BindingsMatchSourceAndRegeneration environment document res reportId ∧
    Admission.ReportAdmitted res ∧
    (∀ S : VE.Structure.{0}, S.Admissible res.src.ne.rv.environment →
      Sat S (VE.Data.Background.generate res.doc.flags) →
      Sat S (background res.src.D ++ elaborate res.src.D.T) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S [])

theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    AdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨envId, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨reportId, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  obtain ⟨hsrc, hbound, hsound, hnodes, hleaves, hcit, hch⟩ :=
    Admission.admitDocument_spec.{0} environment document res hr
  exact ⟨res, reportId, hr, res.src.wf, rfl, hsrc, ⟨hbound, envId, he, hd⟩,
    ⟨hsound, hnodes, hleaves, hcit, hch⟩,
    fun S hS hf hg ho => Admission.norms_wire_report_consequence environment document res hr S hS hf hg ho⟩

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" && usesNormsPath j then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  if kind == "norms-elaborate" then
    let environment ← j.getObjVal? "environment"
    let src ← Wire.decodeSource environment (j.getObjValD "norms") (flags := true)
    return VE.Route.Wire.ok id (Flagged.regenerated src)
  if kind == "norms-certificate" then
    let r ← Flagged.replayEntailment j
    return VE.Route.Wire.ok id [("valid", .bool (Flagged.valid r)),
      ("background", toJson (Flagged.flagPremises r.src ++ background r.src.D).length),
      ("layers", toJson (elaborate r.src.D.T).length)]
  if kind == "norms-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← Flagged.replayWitness j
    return VE.Route.Wire.ok id [("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets src.D).map (·.1)))]
  if kind == "norms-conflict" then
    let res ← Flagged.replayConflict j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("targets", toJson ((targets res.src.D).map (·.1)))] ++
      match Flagged.firstFailure res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  if Plain.isPlainKind kind && (usesNormsPath j || Plain.layered (j.getObjValD "environment"))
      && !(j.getObjVal? "norms").toBool then
    return ← Plain.run j
  if usesNormsPath j || Plain.layered (j.getObjValD "environment") then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the norms route"
  VE.Route.Run.runCase j

/-- The public admission branch (11.4): from raw JSON, a successful norms
admission answer satisfies the full admission obligation for the case's own
id, environment and document; no successful norm input falls through to P0. -/
theorem norms_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesNormsPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      AdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨kind, hkind, h⟩ := VE.Order.ProfileGate.bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [beq_self_eq_true, Bool.true_and, hn, ↓reduceIte] at h
  obtain ⟨environment, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨document, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

def runCaseReported (j : Json) : Json :=
  if usesNormsPath j || Plain.layered (j.getObjValD "environment") then
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
      (← IO.getStderr).putStrLn "usage: ve_norms_route [cases.json|-]"
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

end VE.Norms.Run
