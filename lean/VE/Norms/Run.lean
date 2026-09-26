import VE.Norms.Admission

/-! The `ve_norms_route` executable (docs/spec/norms.md 11.4), invoked as
`lean/.lake/build/bin/ve_norms_route <cases.json|->`. Each case is
`{"id", "environment", "kind", ...}`.

* `norms-elaborate`: `norms` (an array of norm objects, 3.2) → the regenerated
  layer order, Background (with generators), labelled layer premises
  (`layer:norms:<p>`), conflict targets (`p` and `r->m`, with argument sorts)
  and the fragment flag; or the shared diagnostic of `validate`.
* `norms-conflict`: `norms` and `packages` (target → Python's conflict package)
  → `verdict` `CONFLICT-FREE` when every target's certificate is bound and
  accepted over the regenerated `E_base` and `Background_base`, else `UNKNOWN`
  with the first failing target (`Replay.norms_wire_conflict_sound`).
* `norms-conflict` with `witness` (`target`, base `model`, `tuple` of entity ids
  in argument order) → `verdict` `CONFLICT` when the regenerated target formula
  is true at the typed tuple of the validated base model, else `UNKNOWN`
  (`Replay.norms_wire_conflict_witness_sound`).
* `norms-certificate`: `norms`, `premises`, `conclusion`, `certificate` →
  `valid`; the certificate binds the complete environment, the regenerated
  `Background ++ layer premises` followed by `premises`, and the conclusion
  (`Replay.norms_wire_acceptance`).
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

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let report := Json.mkObj [("root", VE.Route.Run.claimJson res.report.root),
    ("assumptions", Json.arr (res.report.assumptions.map VE.Route.Run.claimJson).toArray)]
  let canonical ← Wire.canonicalEnvironmentJson environment
  let envId ← VE.Route.Wire.environmentId res.src.ne.profiles canonical
  let reportId ← VE.CertificateWire.digest
    s!"ve-report-{VE.Route.Wire.identityVersion res.src.ne.profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", document), ("report", report)])
  return VE.Route.Wire.ok id [("admitted", .bool true), ("report", report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray)]

/-- The executable admission result can only arise from a decoded, checked
norm document with admitted leaves and a sound claim graph. -/
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    ∃ res : Admission.Admitted,
      Admission.admitDocument environment document = .ok res ∧
      VE.Graph.SoundReport.{0} res.src.ne.rv.environment res.graph res.report ∧
      (∀ w ∈ res.wires, Admission.NodeAdmitted res.src res.doc w) ∧
      (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
        w.claim = leaf ∧ w.deduction = none ∧ Admission.NodeAdmitted res.src res.doc w) ∧
      (∀ S : VE.Structure.{0}, S.Admissible res.src.ne.rv.environment →
        Sat S (elaborate res.src.D.T) →
        (∀ leaf ∈ res.report.assumptions,
          (¬ ∃ w ∈ res.wires, w.claim = leaf ∧ Admission.LayerLeaf res.src w) →
          leaf.formula.denote S []) → res.report.root.formula.denote S []) := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨hsound, hnodes, hleaves⟩ :=
    Admission.norms_wire_admission_sound environment document res hr
  exact ⟨res, hr, hsound, hnodes, hleaves,
    fun S hS hl ho => Admission.norms_wire_report_consequence environment document res hr S hS hl ho⟩

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" && usesNormsPath j then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  if kind == "norms-elaborate" then
    let environment ← j.getObjVal? "environment"
    let src ← Wire.decodeSource environment (j.getObjValD "norms")
    return VE.Route.Wire.ok id (Wire.regenerated src.D)
  if kind == "norms-certificate" then
    let r ← Replay.replayEntailment j
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("background", toJson (background r.src.D).length), ("layers", toJson (elaborate r.src.D.T).length)]
  if kind == "norms-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← Replay.replayWitness j
    return VE.Route.Wire.ok id [("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets src.D).map (·.1)))]
  if kind == "norms-conflict" then
    let res ← Replay.replayConflict j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("targets", toJson ((targets res.src.D).map (·.1)))] ++
      match Replay.firstFailure res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  if usesNormsPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the norms route"
  VE.Route.Run.runCase j

/-- The public admission branch has the same provenance and graph-soundness
guarantee as `runAdmission`; no successful norm input falls through to P0. -/
theorem norms_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesNormsPath j = true) :
    ∃ res : Admission.Admitted,
      Admission.admitDocument (j.getObjValD "environment")
        (j.getObjValD "document") = .ok res ∧
      VE.Graph.SoundReport.{0} res.src.ne.rv.environment res.graph res.report ∧
      (∀ w ∈ res.wires, Admission.NodeAdmitted res.src res.doc w) ∧
      (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
        w.claim = leaf ∧ w.deduction = none ∧ Admission.NodeAdmitted res.src res.doc w) ∧
      (∀ S : VE.Structure.{0}, S.Admissible res.src.ne.rv.environment →
        Sat S (elaborate res.src.D.T) →
        (∀ leaf ∈ res.report.assumptions,
          (¬ ∃ w ∈ res.wires, w.claim = leaf ∧ Admission.LayerLeaf res.src w) →
          leaf.formula.denote S []) → res.report.root.formula.denote S []) := by
  unfold runCase at h
  obtain ⟨id, _, h⟩ := VE.Order.ProfileGate.bind_ok h
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
  exact runAdmission_sound id environment document answer (by simpa using h)

def runCaseReported (j : Json) : Json :=
  if usesNormsPath j then
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
