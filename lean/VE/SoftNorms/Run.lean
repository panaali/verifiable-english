import VE.SoftNorms.Admission
import VE.Norms.Run

/-! The `ve_soft_norms_route` executable (docs/spec/soft-norms.md 9.4), invoked as
`lean/.lake/build/bin/ve_soft_norms_route <cases.json|->`. Each case is
`{"id", "environment", "kind", ...}`; a `soft-norms@0` environment must also
enable `norms@0`.

* `soft-elaborate`: `norms` → `environment_prime`, `decisions`, `derived`,
  `order`, `background` (with the `soft` slot and its labels), `premises`
  (`layer:norms:<p>` on `T′`), `colliding_pairs`, `conflict_targets`,
  `conditional_on`, `fragment`, `warnings`; or the shared diagnostic.
* `soft-pairs`: `norms` and `pairs` (label → a classification package or a
  `witness`) → per pair RANK-RESOLVED / DISJOINT / WEIGHING POINT / UNKNOWN
  (`Status.lean`), the discharged and open labels.
* `soft-conflict`: `packages` (target → package over `Background_base′`) →
  `CONFLICT-FREE` with `conditional_on`, or `UNKNOWN`
  (`Wire.soft_wire_conflict_sound`); or `witness` → `CONFLICT` classified as a
  strict collision or a pair conflict (`Wire.soft_wire_conflict_witness_sound`).
* `soft-certificate`: `premises`, `conclusion`, `certificate` bound to
  `background′ ++ layer premises ++ premises` over `E′` → `valid`
  (`Wire.soft_wire_acceptance`).
* `admission`: a W2 document with soft norm units (`Run.soft_wire_acceptance`).
* A case without a soft construct is delegated unchanged to W1's
  `Norms.Run.runCase` (which delegates P0 cases to `Route.Run.runCase`); a soft
  input never falls back after a failed soft decode. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire

/-- A soft construct: the `soft-norms@0` profile, the vocabulary's `soft` block, an
`instruction_of`, a soft field on a norm object, or a `soft-*` case kind. -/
def usesSoftPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str softProfile)
    | _ => false
  let vocab := env.getObjValD "vocabulary"
  let block := (vocab.getObjVal? "soft").toBool
  let attributed := match vocab.getObjValD "predicates" with
    | .obj kvs => kvs.toList.any (fun (_, e) => (e.getObjVal? "instruction_of").toBool)
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "soft-"
    | _ => false
  let softField (n : Json) := softKeys.any (fun k => ((n.getObjValD "norm").getObjVal? k).toBool)
  let normsSoft := match j.getObjValD "norms" with
    | .arr ns => ns.toList.any softField
    | _ => false
  let unitSoft := match (j.getObjValD "document").getObjValD "units" with
    | .arr units => units.toList.any (fun u => softField (u.getObjValD "content"))
    | _ => false
  profile || block || attributed || kind || normsSoft || unitSoft

/-! ## Pair classification -/

def classificationPackage (src : SoftSource) (environment norms : Json) (M N : SoftNode) (package : Json) :
    Option VE.Tableau.Certificate := Id.run do
  let label := cohLabel M N
  let some baseEnv := (basePrimeJson src.D environment).toOption | none
  let some baseProfiles := (VE.Bridge.strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (Norms.Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId src.se.profiles canonical).toOption | none
  let some docHash := (softDocumentHash src.se.profiles environment norms).toOption | none
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str label do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((classificationBackground src.D).map enc)
      (enc (cohPremise src.D M N)) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

/-- A weighing-point witness: a base model over `E′_base` passing `Background_base(E′) ++ Exc_T`
and a typed tuple at which both rules select (`weighing_point_sound`). -/
def weighingWitness (src : SoftSource) (M N : SoftNode) (w : Json) : Except String Bool := do
  let ⟨Mo, _⟩ ← decodeModel src w
  unless classificationBackgroundValid src.D Mo do throw (VE.Route.Wire.invalidModel "soft background")
  let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
  let sorts := actSorts src.D M
  let tuple := sorts.zip ids
  unless ids.length == sorts.length && VE.Bridge.tupleCheck Mo sorts tuple do
    throw "InvalidInput: witness tuple has the wrong length or sort"
  pure ((VE.Formula.and (circ src.D (selects' src.D M)) (circ src.D (selects' src.D N))).eval Mo (tupleVal tuple))

def classify (src : SoftSource) (environment norms pairs : Json) (M N : SoftNode) :
    Except String (PairStatus × String) := do
  if Comparable src.D M N then return (.rankResolved, "")
  let evidence := pairs.getObjValD (cohLabel M N)
  if (evidence.getObjVal? "witness").toBool then
    if ← weighingWitness src M N (evidence.getObjValD "witness") then return (.weighingPoint, "witness")
    else return (.unknown, "witness does not select both rules")
  if (evidence.getObjVal? "certificate").toBool then
    match classificationPackage src environment norms M N evidence with
    | some c =>
      if VE.Tableau.checkCertificate (envAt (soften src.D) 0) (classificationBackground src.D)
          (cohPremise src.D M N) c then return (.disjoint, "")
      else return (.unknown, "invalid certificate")
    | none => return (.unknown, "unbound certificate")
  return (.unknown, "no evidence")

def pairsResult (src : SoftSource) (environment norms pairs : Json) : Except String (List (String × Json)) := do
  let rows ← (collidingPairs src.D).mapM fun (M, N) => do
    let (st, detail) ← classify src environment norms pairs M N
    pure (cohLabel M N, st, Json.mkObj ([("pair", toJson [M.name, N.name]), ("label", .str (cohLabel M N)),
      ("status", .str st.text)] ++ (if detail.isEmpty then [] else [("detail", .str detail)])))
  let discharged := rows.filterMap (fun (l, st, _) =>
    if st == .rankResolved || st == .disjoint then some l else none)
  let open_ := rows.filterMap (fun (l, st, _) =>
    if st == .rankResolved || st == .disjoint then none else some l)
  pure [("pairs", Json.arr (rows.map (·.2.2)).toArray), ("discharged", toJson discharged),
    ("weighing_points", toJson open_)]

/-! ## Admission -/

/-- The answer for an admitted document: W1's fields and `conditional_on`. -/
def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson (Admission.conditionalOn res))]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let canonical ← Norms.Wire.canonicalEnvironmentJson environment
  let envId ← VE.Route.Wire.environmentId res.src.se.profiles canonical
  let reportId ← VE.CertificateWire.digest (Norms.Run.reportDomain res.src.se.profiles)
    (Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

/-- Every binding is the recomputed one: certificates name the regenerated `E′` and their source
ASTs, and the report id is the digest of the canonical environment id, the complete source
document and the checked report. -/
def BindingsMatchSourceAndRegeneration (environment document : Json) (res : Admission.Admitted)
    (reportId : String) : Prop :=
  Admission.CertificatesBound environment res ∧
  ∃ canonical envId, Norms.Wire.canonicalEnvironmentJson environment = .ok canonical ∧
    VE.Route.Wire.environmentId res.src.se.profiles canonical = .ok envId ∧
    VE.CertificateWire.digest (Norms.Run.reportDomain res.src.se.profiles)
      (Norms.Run.reportPayload envId document res.report) = .ok reportId

/-- W1's `AdmissionAnswer` with the soft decoder: the answer is exactly the encoding of a
checked admission whose bindings equal the recomputed digests and the regenerated `E′`, `T′`,
layer, `background:profile` and `soft:*` leaves, and whose report follows from
`background′ ++ elaborate T′` and its remaining assumptions. -/
def SoftAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormedSoft res.src.D = true ∧
    answer = encodeAdmitted id reportId res ∧
    Admission.SourceDecoded environment document res ∧
    BindingsMatchSourceAndRegeneration environment document res reportId ∧
    Admission.ReportAdmitted res ∧
    (∀ S : VE.Structure.{0}, S.Admissible (envPrime res.src.D) →
      Sat S (VE.Data.Background.generate res.doc.flags) →
      Sat S (background' res.src.D ++ elaborate (soften res.src.D).T) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S [])

open VE.Order.ProfileGate (bind_ok) in
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    SoftAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hsrc, hbound, hsound, hnodes, hleaves, hcit, hch⟩ :=
    Admission.admitDocument_spec.{0} environment document res hr
  exact ⟨res, reportId, hr, res.src.wf, rfl, hsrc, ⟨hbound, canonical, envId, hc, he, hd⟩,
    ⟨hsound, hnodes, hleaves, hcit, hch⟩,
    fun S hS hf hg ho => Admission.soft_wire_report_consequence environment document res hr S hS hf hg ho⟩

/-! ## Dispatch -/

def witnessKind (t : String × List String × VE.Formula) : String :=
  if (t.1.splitOn "->").length > 1 then s!"pair conflict on {t.1}" else s!"strict collision on {t.1}"

/-- The non-admission soft case kinds. -/
def runSoftKind (id kind : String) (j : Json) : Except String Json := do
  if kind == "soft-elaborate" then
    let environment ← j.getObjVal? "environment"
    let src ← decodeSoftSource environment (j.getObjValD "norms")
    return VE.Route.Wire.ok id (regenerated src.D environment)
  if kind == "soft-pairs" then
    let environment ← j.getObjVal? "environment"
    let norms := j.getObjValD "norms"
    let src ← decodeSoftSource environment norms
    return VE.Route.Wire.ok id (← pairsResult src environment norms (j.getObjValD "pairs"))
  if kind == "soft-certificate" then
    let r ← replaySoftEntailment j
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("background", toJson (background' r.src.D).length), ("layers", toJson (elaborate (soften r.src.D).T).length),
      ("conditional_on", toJson (openCoherence r.src.D))]
  if kind == "soft-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← replaySoftWitness j
    return VE.Route.Wire.ok id ([("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets (soften src.D)).map (·.1)))] ++
      (if w.conflict then [("witness_kind", .str (witnessKind w.target))] else []))
  if kind == "soft-conflict" then
    let res ← replaySoftConflict j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("targets", toJson ((targets (soften res.src.D)).map (·.1))),
      ("conditional_on", toJson (openCoherence res.src.D))] ++
      match firstFailure res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  throw s!"UnsupportedProfile: case kind {kind} is not available on the soft-norms route"

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" && usesSoftPath j then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  if !usesSoftPath j then return ← Norms.Run.runCase j
  runSoftKind id kind j

open VE.Order.ProfileGate (bind_ok) in
/-- The public admission branch: from raw JSON, a successful soft `admission` answer satisfies
the full admission obligation for the case's own id, environment and document; no successful
soft input falls through to W1 or P0. -/
theorem soft_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesSoftPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      SoftAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
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
  if usesSoftPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else Norms.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_soft_norms_route [cases.json|-]"
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

end VE.SoftNorms.Run
