import ResponseShape.Encoders.Route

/-! The `reports` mode (`Reports.Run.runCaseReported`) against `reports.json#/row`. A case off the
reports path is the route mode's. -/

namespace ResponseShape.Encoders.Reports
open Lean ResponseShape ResponseShape.Skeletons
open VE.Reports VE.Reports.Run

variable {req : Json}

theorem of_route {v : Json} (h : Fits req Skeletons.route v) : Fits req Skeletons.reports v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem generated_key (D : ReportDoc) (x : String × List String × Json) (h : x ∈ Wire.generated D) :
    Fits req (skel% "reports.json#/$defs/key") x.2.2 := by
  simp only [Wire.generated, List.mem_append, List.mem_map] at h
  rcases h with ⟨k, _, rfl⟩ | ⟨k, _, rfl⟩ <;> fits

theorem elaborate_fits (id : String) (dec : Wire.Decoded) (environment : Json) :
    Fits req Skeletons.reports (VE.Route.Wire.ok id (elaborated dec environment)) := by
  unfold VE.Route.Wire.ok elaborated envelopeJson recordJson
  simp only []
  fits using generated_key

theorem content_fits (id meaningId : String) :
    Fits req Skeletons.reports (VE.Route.Wire.ok id [("meaning_id", .str meaningId)]) := by
  simp only [VE.Route.Wire.ok]
  fits

theorem certificate_fits (c : Wire.Checked) (environment : Json) (id : String) (j : Json) :
    OkFits req Skeletons.reports (runCertificate c environment id j) := by
  unfold runCertificate
  okfits
  simp only [VE.Route.Wire.ok, envelopeJson]
  fits

theorem countermodel_fits (c : Wire.Checked) (id : String) (j : Json) :
    OkFits req Skeletons.reports (runCountermodel c id j) := by
  unfold runCountermodel
  okfits
  simp only [countermodelAnswer, VE.Route.Wire.ok]
  fits using generated_key

theorem scopedVerdict_fits (c : Wire.Checked) (j : Json) (s : ScopedCheck) :
    OkFits req (skel% "reports.json#/$defs/verdict") (scopedVerdict c j s) := by
  unfold scopedVerdict
  okfits
  all_goals fits

theorem scopedUnreplayed_fits (c : Wire.Checked) (j : Json) (s : ScopedCheck) :
    Fits req (skel% "reports.json#/$defs/verdict") (scopedUnreplayed c j s) := by
  unfold scopedUnreplayed
  split <;> fits

theorem nested_fits (D : ReportDoc) (u : Wire.DecodedUnit) (x : Json × Status)
    (h : x ∈ nestedResults D u) :
    Fits req (skel% "reports.json#/$defs/nested") x.fst := by
  simp only [nestedResults, List.mem_append] at h
  rcases h with (h | h) | h
  · cases u with
    | reports x start stop kind =>
        simp only [List.mem_map] at h
        rcases h with ⟨p, _, rfl⟩
        fits
    | w2 x => simp at h
  · simp only [List.mem_map] at h
    rcases h with ⟨p, _, rfl⟩
    fits
  · simp only [List.mem_map] at h
    rcases h with ⟨p, _, rfl⟩
    fits

theorem status_fits (c : Wire.Checked) (id : String) (j : Json) :
    OkFits req Skeletons.reports (runStatus c id j) := by
  unfold runStatus
  okfits
  simp only [VE.Route.Wire.ok, envelopeJson, nestedResults]
  all_goals fits_as "reports.json#/$defs/status"
  all_goals fits using scopedUnreplayed_fits
  all_goals fits using nested_fits
  all_goals fits
  all_goals try (exact OkP.mapM (fun x _ => scopedVerdict_fits c j x) _ (by assumption) _ (by assumption))

theorem admission_fits (id reportId : String) (res : ReportsAdmitted) :
    Fits req Skeletons.reports (encodeAdmitted id reportId res) := by
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

theorem runCase_fits (j : Json) : OkFits req Skeletons.reports (runCase j) := by
  unfold runCase
  simp only []
  okfits
  · unfold runAdmission
    okfits
    exact admission_fits _ _ _
  · exact elaborate_fits _ _ _
  · exact content_fits _ _
  · exact certificate_fits _ _ _ _
  · exact countermodel_fits _ _ _
  · fits_as "reports.json#/$defs/scoped"
    exact scoped_fits _ _ _ _ ‹_›
  · exact status_fits _ _ _
  all_goals exact OkP.of (Route.runCase_fits _) fun _ => of_route

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.reports (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_route (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Reports
