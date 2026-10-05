import ResponseShape.Encoders.Alternatives

/-! The `risk` mode (`Risk.Run.runCaseReported`) against `risk.json#/row`. A case off the risk path
is the alternatives mode's. -/

namespace ResponseShape.Encoders.Risk
open Lean ResponseShape ResponseShape.Skeletons
open VE.Risk VE.Risk.Run

variable {req : Json}

theorem of_alternatives {v : Json} (h : Fits req Skeletons.alternatives v) : Fits req Skeletons.risk v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem decision_fits (id : String) (j : Json) : OkFits req Skeletons.risk (runDecision id j) := by
  unfold runDecision
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok, endpointJson, caseJson])
  all_goals fits

theorem conflict_fits (id : String) (j : Json) : OkFits req Skeletons.risk (runConflict id j) := by
  unfold runConflict
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem followable_fits (id : String) (j : Json) : OkFits req Skeletons.risk (runFollowable id j) := by
  unfold runFollowable
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem audit_fits (id : String) (j : Json) : OkFits req Skeletons.risk (runAudit id j) := by
  unfold runAudit
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem certificate_fits (id : String) (j : Json) : OkFits req Skeletons.risk (runCertificate id j) := by
  unfold runCertificate
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem elaborate_fits (id : String) (src : Wire.RiskSource) :
    Fits req Skeletons.risk (ok id (Wire.regenerated src)) := by
  unfold ok VE.Route.Wire.ok Wire.regenerated VE.Alternatives.Wire.encodeNode Wire.labelled
    VE.Norms.Wire.regenerated orWorseName lessWorstName
  simp only []
  fits

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits req Skeletons.risk (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted ok VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

theorem runCase_fits (j : Json) : OkFits req Skeletons.risk (runCase j) := by
  unfold runCase
  okfits
  all_goals first
    | (unfold runAdmission; okfits; exact admission_fits _ _ _)
    | with_reducible exact elaborate_fits _ _
    | with_reducible exact decision_fits _ _
    | with_reducible exact conflict_fits _ _
    | with_reducible exact followable_fits _ _
    | with_reducible exact audit_fits _ _
    | with_reducible exact certificate_fits _ _

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.risk (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_alternatives (Alternatives.runCaseReported_fits j)

end ResponseShape.Encoders.Risk
