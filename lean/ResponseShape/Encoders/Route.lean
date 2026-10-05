import ResponseShape.Encoders.Common

/-! The `route` mode (`Route.Run.runCaseReported`) against `route.json#/row`. -/

namespace ResponseShape.Encoders.Route
open Lean ResponseShape ResponseShape.Skeletons
open VE.Route VE.Route.Run

variable {req : Json}

theorem runBackground_fits (id : String) (bg : List (VE.Formula × String)) :
    Fits req Skeletons.route (Wire.runBackground id bg) := by
  unfold Wire.runBackground Wire.ok
  fits

theorem runDependencyOrder_fits (id : String) (j : Json) :
    OkFits req Skeletons.route (Wire.runDependencyOrder id j) := by
  unfold Wire.runDependencyOrder
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits

theorem runFol_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id kind : String)
    (j : Json) (hk : ¬ (kind == "background") = true) :
    OkFits req Skeletons.route (Wire.runFol profiles environment rv id kind j) := by
  unfold Wire.runFol
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits
  all_goals contradiction

theorem runClosure_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id kind : String)
    (j : Json) (hk : ¬ (kind == "background") = true) :
    OkFits req Skeletons.route (Wire.runClosure profiles environment rv id kind j) := by
  unfold Wire.runClosure
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits
  all_goals contradiction

theorem runOrder_fits (profiles : List String) (environment : Json) (rv : Wire.RouteOrderVocabulary)
    (id kind : String) (j : Json) :
    OkFits req Skeletons.route (Wire.runOrder profiles environment rv id kind j) := by
  unfold Wire.runOrder
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits

theorem coreWire_fits (profiles : List String) (environment : Json) (id kind : String) (j : Json) :
    OkFits req Skeletons.route (VE.Core.Wire.run profiles environment id kind j) := by
  unfold VE.Core.Wire.run
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals first | with_reducible exact runBackground_fits _ _ | fits

theorem coreLayers_fits (profiles : List String) (environment : Json) (id kind : String) (j : Json) :
    OkFits req Skeletons.route (VE.Core.Layers.run profiles environment id kind j) := by
  unfold VE.Core.Layers.run
  okfits
  all_goals first
    | with_reducible exact runBackground_fits _ _
    | with_reducible exact coreWire_fits _ _ _ _ _
    | (unfold VE.Core.Layers.coreCertificate; okfits; all_goals (try simp only [Wire.ok]); all_goals fits)

theorem runBundle_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) : OkFits req Skeletons.route (VE.Definitions.Bundle.runBundle profiles environment rv id j) := by
  unfold VE.Definitions.Bundle.runBundle
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits

theorem runAdmit_fits (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) : OkFits req Skeletons.route (runAdmit profiles environment rv id j) := by
  unfold runAdmit
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals fits
  all_goals exact Common.claimJson_fits _

theorem dispatch_fits (id : String) (environment : Json) (e : Gate.Envelope) (j : Json) :
    OkFits req Skeletons.route (dispatch id environment e j) := by
  unfold dispatch
  okfits
  all_goals (try simp only [Wire.ok])
  all_goals first
    | with_reducible exact runDependencyOrder_fits _ _
    | with_reducible exact coreLayers_fits _ _ _ _ _
    | with_reducible exact coreWire_fits _ _ _ _ _
    | with_reducible exact runBackground_fits _ _
    | with_reducible exact runOrder_fits _ _ _ _ _ _
    | with_reducible exact runClosure_fits _ _ _ _ _ _ ‹_›
    | with_reducible exact runBundle_fits _ _ _ _ _
    | with_reducible exact runAdmit_fits _ _ _ _ _
    | with_reducible exact runFol_fits _ _ _ _ _ _ ‹_›
    | fits

theorem runCase_fits (j : Json) : OkFits req Skeletons.route (runCase j) := by
  unfold runCase
  okfits
  exact dispatch_fits _ _ _ _

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.route (runCaseReported j) := by
  unfold runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits
    -- `valid` exactly beside a certificate case: the row's test of the case is the shape's.
    all_goals case_cond

end ResponseShape.Encoders.Route
