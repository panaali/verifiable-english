import ResponseShape.Encoders.Route

/-! The `reports` mode (`Reports.Run.runCaseReported`) against `reports.json#/row`. A case off the
reports path is the route mode's. -/

namespace ResponseShape.Encoders.Reports
open Lean ResponseShape ResponseShape.Skeletons
open VE.Reports VE.Reports.Run

variable {req : Json}

/-- The route mode's rows, off the reports path, are rows of this mode. -/
theorem of_route {v : Json} (hp : usesReportsPath req = false) (h : Fits req Skeletons.route v) :
    Fits req Skeletons.reports v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

theorem generated_key (D : ReportDoc) (x : String × List String × Json) (h : x ∈ Wire.generated D) :
    Fits req (skel% "reports.json#/$defs/key") x.2.2 := by
  simp only [Wire.generated, List.mem_append, List.mem_map] at h
  rcases h with ⟨k, _, rfl⟩ | ⟨k, _, rfl⟩ <;> fits

theorem elaborate_fits (id : String) (dec : Wire.Decoded) (environment : Json) :
    Fits req (skel% "reports.json#/$defs/elaborate") (VE.Route.Wire.ok id (elaborated dec environment)) := by
  unfold VE.Route.Wire.ok elaborated envelopeJson recordJson
  simp only []
  fits using generated_key

theorem certificate_fits (c : Wire.Checked) (environment : Json) (id : String) (j : Json) :
    OkFits req (skel% "reports.json#/$defs/certificate") (runCertificate c environment id j) := by
  unfold runCertificate
  okfits
  simp only [VE.Route.Wire.ok, envelopeJson]
  fits

theorem countermodel_fits (c : Wire.Checked) (id : String) (j : Json) :
    OkFits req (skel% "reports.json#/$defs/countermodel") (runCountermodel c id j) := by
  unfold runCountermodel
  okfits
  simp only [countermodelAnswer, VE.Route.Wire.ok]
  fits using generated_key

theorem scopedVerdict_fits (c : Wire.Checked) (j : Json) (s : ScopedCheck) :
    OkFits req (skel% "reports.json#/$defs/verdict") (scopedVerdict c j s) := by
  unfold scopedVerdict
  okfits
  all_goals fits

theorem status_fits (c : Wire.Checked) (id : String) (j : Json) :
    OkFits req (skel% "reports.json#/$defs/status") (runStatus c id j) := by
  unfold runStatus
  okfits
  simp only [VE.Route.Wire.ok, envelopeJson, nestedResults]
  fits
  exact OkP.mapM (fun x _ => scopedVerdict_fits c j x) _ ‹_› _ ‹_›

theorem admission_fits (id reportId : String) (res : ReportsAdmitted) :
    Fits req (skel% "reports.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok reportJson
  fits
  all_goals exact Common.claimJson_fits _

theorem scoped_fits (c : Wire.Checked) (j : Json) (id : String) (verdicts : List Json)
    (h : c.dec.D.«scoped».mapM (scopedVerdict c j) = .ok verdicts) :
    Fits req (skel% "reports.json#/$defs/scoped") (VE.Route.Wire.ok id [("scoped", Json.arr verdicts.toArray),
      ("envelope", envelopeJson c.dec.D c.dec.D.environmentId),
      ("bindings", Json.mkObj [("envelope", .bool (outerBound c.dec.D j))])]) := by
  simp only [VE.Route.Wire.ok, envelopeJson]
  fits
  exact OkP.mapM (fun x _ => scopedVerdict_fits _ j x) _ h _ ‹_›

theorem runCase_fits (j : Json) (hp : usesReportsPath j = true) : OkFits j Skeletons.reports (runCase j) := by
  unfold runCase
  simp only []
  okfits
  all_goals first
    | contra
    | read_kind
  all_goals (try contra)
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _)
    | fits_from elaborate_fits _ _ _
    | (intro v hv; fits_from certificate_fits _ _ _ _ _ hv)
    | (intro v hv; fits_from countermodel_fits _ _ _ _ hv)
    | fits_from scoped_fits _ _ _ _ ‹_›
    | (intro v hv; fits_from status_fits _ _ _ _ hv)

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.reports (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_route (Bool.eq_false_iff.mpr ‹_›) (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Reports
