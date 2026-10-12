import VE.NormDefaults.Layered
import VE.NormDefaults.LayeredAdmission
import VE.NormDefaults.Admission
import VE.NormDefaults.Explain
import VE.Norms.Run

/-! The `ve_service` mode `norm-defaults` (docs/spec/norm-defaults.md 3, 6 and 8), formerly the one-shot `ve_norm_defaults_route`. The frozen
norms route is unchanged; this executable adds the `norm-defaults@0` branch and
delegates every other case to it.

* `norm-defaults-elaborate`: `norms` → the regenerated outputs of `fill U`
  (`Wire.regeneratedU`), or the decoder's diagnostic.
* `norm-defaults-conflict`: `norms` and `packages` (target of `fill U` → package)
  → `CONFLICT-FREE` when every target's certificate is bound and accepted over
  `E‴_base` and `Background_base(E‴) ++ Fill_T` (`Wire.normDefaults_wire_conflict_sound`),
  else `UNKNOWN` with the first failing target.
* `norm-defaults-conflict` with `witness` (`target`, a `model` of `E‴_base` whose
  `unsaid__` tables are the filling, `tuple`) → `CONFLICT` when the model passes
  `Background_base` and `Fill_T` and the target is true at the tuple
  (`Wire.normDefaults_wire_witness_sound`: settled or latent), else `UNKNOWN`. A CONFLICT
  also carries what its English needs (`Explain.lean`): the `tuple`, the `kind`, the
  deciding assignment `under` (`Wire.underOf_sufficient`) and the deciding author `rules`.
* `norm-defaults-status`: a base `model`, `predicate`, `tuple` and `method`
  (`table3`, `enumerate`, or `undecided` with fillings `yes` and `no`) → `point_status`
  `SETTLED yes|no`, `UNDECIDED` or `UNKNOWN` (`Wire.normDefaults_wire_status_sound`), with
  the `tuple`, the deciding author `rules` and, when UNDECIDED, the atoms where the two
  fillings `differs` (`Wire.statusFields`).
* `norm-defaults-gaps`: `predicate` and `packages` (key `reached:<p>`) → `gaps: none`
  when the certificate for `∀x̄. ¬reached_p` is bound and accepted
  (`Wire.normDefaults_wire_gaps_sound`), else `unknown`; with a filled `model` and
  `tuple` → `reachable` when `reached_p` is true there (`Wire.normDefaults_wire_reached_sound`).
* `norm-defaults-report`: the 3.2 lines of every regulated predicate (`Report.lean`,
  `Wire.normDefaults_wire_report_sound`): `completion`, `gaps`/`default reached`
  (`reachable` from the supplied base `model`, searched here, or a supplied filled
  `witnesses` entry, with the completed `value` there, `Wire.value3_gap`; `none` from a
  `reached:<p>` package; else `unknown`), the
  `completions` grounding or `UngroundedDefault` (with `translation`), `inherits_from`,
  and the residual `gaps` and `ungrounded_defaults`.
* The soft and rights branches (`Layered.lean`): under the profile with `soft-norms@0`
  (source `norms`) or `rights@0` (source `document`), the `norm-defaults-elaborate`,
  `-conflict` (packages or a filled `witness`), `-status` and `-report` kinds run on
  `fill (soften T)` or `fill (soften (correlate D))` with the route's base premises
  (`Wire.layered_conflict_sound`, `Wire.layered_report_sound`); evidence is a base
  situation `model` with a separate `filling`.
* `norm-defaults-certificate`: `norms`, `premises`, `conclusion`, `certificate` →
  `valid` over `Background(E‴) ++ Fill_T ++ layer premises of T‴ ++ premises`
  (`Wire.normDefaults_wire_acceptance`).
* `admission` under the profile: a W2 FOL `document` with norm units → W1's
  admission answer on `fill U` (`Admission.admitDocument`, `normDefaults_wire_admission`):
  graph nodes over `E‴`, certificates bound to the regenerated `E‴` JSON, and
  leaves that are W2 provenance or exactly a regenerated layer of `T‴`, pair
  premise or `Fill_T` premise (`unsaid:pair:<r>,<m>`).
* A case with the profile or an `unspecified` default but another kind is
  `UnsupportedProfile`; every other case goes to `VE.Norms.Run.runCase`. -/
namespace VE.NormDefaults.Run
open Lean

/-- A norm-defaults construct: the profile, an `unspecified` default, or a
`norm-defaults-*` case kind. -/
def usesNormDefaultsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "norm-defaults-"
    | _ => false
  Wire.hasProfile env || !(Wire.unspecifiedNames env).isEmpty || kind

/-- The first target of `fill U` without an accepted certificate. -/
def firstFailureU (r : Wire.ConflictReplayU) : Option String :=
  (((VE.Norms.targets (fill r.s.U)).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (VE.Norms.envAt (fill r.s.U) 0) (Wire.baseBackgroundU r.s.U)
        (VE.Norms.targetConclusion t) c
    | none => true)).map (fun (t, c) =>
      if c.isSome then s!"invalid certificate for {t.1}" else s!"missing certificate for {t.1}")

/-! ## Admission -/

/-- The answer for an admitted document: W1's fields. -/
def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", VE.Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray)]

/-- The report id is bound to the source environment under its own profiles
(`norm-defaults@0` included), as the norms route binds it and as conflict packages
are bound (`decodePackageU`); certificates are bound to the regenerated `E‴`. -/
def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let canonical ← Wire.canonicalEnvironmentJsonU environment
  let envId ← VE.Route.Wire.environmentId (Wire.profilesOf environment) canonical
  let reportId ← VE.CertificateWire.digest (VE.Norms.Run.reportDomain (Wire.profilesOf environment))
    (VE.Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

def BindingsMatchSourceAndRegeneration (environment document : Json) (res : Admission.Admitted)
    (reportId : String) : Prop :=
  Admission.CertificatesBound environment res ∧
  ∃ canonical envId, Wire.canonicalEnvironmentJsonU environment = .ok canonical ∧
    VE.Route.Wire.environmentId (Wire.profilesOf environment) canonical = .ok envId ∧
    VE.CertificateWire.digest (VE.Norms.Run.reportDomain (Wire.profilesOf environment))
      (VE.Norms.Run.reportPayload envId document res.report) = .ok reportId

/-- W1's `AdmissionAnswer` on `fill U`: the answer is exactly the encoding of a checked
admission whose bindings equal the recomputed digests and the regenerated `E‴`, and
whose report follows from the Background of `fill U`, `Fill_T`, the layers of `T‴`
and its remaining assumptions. -/
def AdmissionAnswerU (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormedU res.s.U = true ∧
    answer = encodeAdmitted id reportId res ∧
    Admission.SourceDecoded environment document res ∧
    BindingsMatchSourceAndRegeneration environment document res reportId ∧
    Admission.ReportAdmitted res ∧
    (∀ S : VE.Structure.{0}, S.Admissible (fill res.s.U).E →
      VE.Norms.Sat S (VE.Data.Background.generate res.doc.flags) →
      VE.Norms.Sat S (VE.Norms.background (fill res.s.U) ++ fillPremises res.s.U ++
        VE.Norms.elaborate (fill res.s.U).T) →
      VE.Norms.Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S [])

open VE.Order.ProfileGate (bind_ok) in
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    AdmissionAnswerU id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hsrc, hbound, hsound, hnodes, hleaves, hcit, hch⟩ :=
    Admission.admitDocument_spec.{0} environment document res hr
  exact ⟨res, reportId, hr, res.s.wfU hsrc.2.1, rfl, hsrc, ⟨hbound, canonical, envId, hc, he, hd⟩,
    ⟨hsound, hnodes, hleaves, hcit, hch⟩,
    fun S hS hf hg ho =>
      Admission.wire_report_consequence environment document res hr S hS hf hg ho⟩

/-- Every case but a profiled admission. -/
def runOtherCase (id kind : String) (j : Json) : Except String Json := do
  let env := j.getObjValD "environment"
  if !Wire.hasProfile env && !(Wire.unspecifiedNames env).isEmpty then
    throw "UnsupportedProfile: unspecified completion requires norm-defaults@0"
  if Wire.hasProfile env && (Wire.layeredRoute env).isSome && kind.startsWith "norm-defaults-" then
    return ← Wire.runLayered id kind j
  if kind == "norm-defaults-elaborate" then
    let environment ← j.getObjVal? "environment"
    let s ← Wire.decodeSourceU environment (j.getObjValD "norms")
    let filled ← Admission.fillJson environment s.U
    let filledId ← VE.Route.Wire.environmentId (Wire.profilesOf filled) filled
    let sourceId ← VE.Route.Wire.environmentId (Wire.profilesOf environment)
      (← Wire.canonicalEnvironmentJsonU environment)
    let documentHash ← VE.Norms.Replay.documentHash (Wire.profilesOf environment)
      environment (j.getObjValD "norms")
    let labelled := Json.arr ((Admission.fillLabelled s.U).map (fun (label, formula) =>
      Json.arr #[.str label, Wire.enc formula])).toArray
    let fillHash ← VE.CertificateWire.digest
      s!"ve-norm-defaults-fill-{VE.Route.Wire.identityVersion (Wire.profilesOf environment)}\n"
      (Json.mkObj [("environment_id", .str sourceId), ("premises", labelled)])
    return VE.Route.Wire.ok id (Wire.regeneratedU s.U ++
      [("filled_environment_id", .str filledId), ("fill_hash", .str fillHash),
       ("fill_labels", toJson (Admission.fillLabels s.U)),
       ("environment_id", .str sourceId), ("document_hash", .str documentHash)])
  if kind == "norm-defaults-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨s, w⟩ ← Wire.replayWitnessU j
    return VE.Route.Wire.ok id ([("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((VE.Norms.targets (fill s.U)).map (·.1)))] ++
      if w.conflict then Wire.conflictFields s.U w.M w.target.1 w.target.2.2 w.tuple else [])
  if kind == "norm-defaults-status" then
    let d ← Wire.replayStatus j
    let fillings ← if d.status = .undecided then
        some <$> ((·, ·) <$> Wire.decodeFilling d.s.U d.M (j.getObjValD "yes") <*>
          Wire.decodeFilling d.s.U d.M (j.getObjValD "no"))
      else pure none
    return VE.Route.Wire.ok id ([("point_status", .str d.status.label), ("predicate", .str d.r.name)] ++
      Wire.statusFields d.s.U d.M d.r.name d.tuple (d.status != .undecided && d.status != .unknown) fillings)
  if kind == "norm-defaults-gaps" && (j.getObjVal? "model").toBool then
    let ⟨_, d⟩ ← Wire.replayReached j
    return VE.Route.Wire.ok id [("gaps", .str (if d.reached then "reachable" else "unknown")),
      ("predicate", .str d.r.name)]
  if kind == "norm-defaults-gaps" then
    let g ← Wire.replayGaps j
    return VE.Route.Wire.ok id [("gaps", .str (if g.none_ then "none" else "unknown")),
      ("predicate", .str g.r.name)]
  if kind == "norm-defaults-conflict" then
    let res ← Wire.replayConflictU j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("targets", toJson ((VE.Norms.targets (fill res.s.U)).map (·.1)))] ++
      match firstFailureU res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  if kind == "norm-defaults-report" then
    let rep ← Wire.reportFrom j
    return VE.Route.Wire.ok id rep.rep.toJson
  if kind == "norm-defaults-certificate" then
    let r ← Wire.replayEntailmentU j
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("premises", toJson (Wire.premisesU r.s.U []).length)]
  if usesNormDefaultsPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the norm-defaults route"
  VE.Norms.Run.runCase j

/-- The soft branch's `admission` and `norm-defaults-certificate` (`Admission.softCase`) first, for a soft source
under the profile; then a profiled admission on the norms branch; then every other case. -/
def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  let env := j.getObjValD "environment"
  if Wire.hasProfile env && Wire.layeredRoute env == some "soft-norms@0" then
    if let some a ← Admission.softCase id kind j then return a
  if kind == "admission" && Wire.hasProfile env then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  runOtherCase id kind j

/-- The public admission branch: from raw JSON under the profile, a successful answer
satisfies the full admission obligation on `fill U` for the case's own id, environment
and document; no profiled admission falls through to the norms route. The soft branch
(`layeredRoute = some "soft-norms@0"`) is `normDefaults_wire_admissionX`'s. -/
theorem normDefaults_wire_admission (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : Wire.hasProfile (j.getObjValD "environment") = true)
    (hs : Wire.layeredRoute (j.getObjValD "environment") ≠ some "soft-norms@0") :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      AdmissionAnswerU id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨kind, hkind, h⟩ := VE.Order.ProfileGate.bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  have hs' : (Wire.layeredRoute (j.getObjValD "environment") == some "soft-norms@0") = false := by
    simpa using hs
  simp only [beq_self_eq_true, Bool.true_and, hp, hs', Bool.and_false, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨environment, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨document, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

/-- The soft branch's admission: from raw JSON under the profile with a soft source, a successful answer satisfies
the full admission obligation on the filled soft tree (`Admission.AdmissionAnswerX`) for the case's own id,
environment and document. With `normDefaults_wire_admission` it covers every profiled admission. -/
theorem normDefaults_wire_admissionX (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : Wire.hasProfile (j.getObjValD "environment") = true)
    (hs : Wire.layeredRoute (j.getObjValD "environment") = some "soft-norms@0") :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      Admission.AdmissionAnswerX id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨kind, hkind, h⟩ := VE.Order.ProfileGate.bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [hp, hs, beq_self_eq_true, Bool.and_self, ↓reduceIte] at h
  obtain ⟨o, ho, h⟩ := VE.Order.ProfileGate.bind_ok h
  unfold Admission.softCase at ho
  simp only [beq_self_eq_true, ↓reduceIte] at ho
  obtain ⟨environment, he, ho⟩ := VE.Order.ProfileGate.bind_ok ho
  obtain ⟨document, hd, ho⟩ := VE.Order.ProfileGate.bind_ok ho
  obtain ⟨a, ha, ho⟩ := VE.Order.ProfileGate.bind_ok ho
  cases ho
  cases h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, Admission.runAdmissionX_sound id environment document answer ha⟩

def runCaseReported (j : Json) : Json :=
  if usesNormDefaultsPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.Norms.Run.runCaseReported j

end VE.NormDefaults.Run
