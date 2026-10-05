import ResponseShape.Encoders.Route

/-! The `norms` mode (`Norms.Run.runCaseReported`) against `norms.json#/row`. A case off the norms
path is the route mode's. -/

namespace ResponseShape.Encoders.Norms
open Lean ResponseShape ResponseShape.Skeletons
open VE.Norms VE.Norms.Run

variable {req : Json}

theorem of_route {v : Json} (h : Fits req Skeletons.route v) : Fits req Skeletons.norms v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits req Skeletons.norms (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

theorem certificate_fits (profiles : List String) (environment stripped : Json) (T : Tree)
    (extra : List VE.Formula) (id : String) (j : Json) :
    OkFits req Skeletons.norms (Plain.certificate profiles environment stripped T extra id j) := by
  unfold Plain.certificate Plain.folCertificate Plain.closureCertificate Plain.orderCertificate
    VE.Core.Layers.coreCertificate
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals first
    | with_reducible exact OkP.of (Route.runOrder_fits _ _ _ _ _ _) fun _ => of_route
    | fits

theorem plain_fits (j : Json) : OkFits req Skeletons.norms (Plain.run j) := by
  unfold Plain.run
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals first
    | with_reducible exact certificate_fits _ _ _ _ _ _ _
    | exact of_route (Route.runCase_fits _ _ ‹_›)
    | fits

theorem runCase_fits (j : Json) : OkFits req Skeletons.norms (runCase j) := by
  unfold runCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok, Flagged.regenerated, Wire.regenerated, List.map_cons, List.map_nil,
    String.reduceBEq])
  all_goals first
    | (unfold runAdmission; okfits; exact admission_fits _ _ _)
    | with_reducible exact plain_fits _
    | with_reducible exact OkP.of (Route.runCase_fits _) fun _ => of_route
    | fits

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.norms (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_route (Route.runCaseReported_fits j)

end ResponseShape.Encoders.Norms
