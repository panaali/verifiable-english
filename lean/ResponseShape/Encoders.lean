import ResponseShape.Encoders.Conformance
import ResponseShape.Encoders.English
import ResponseShape.Encoders.Standalone
import ResponseShape.Encoders.Family
import ResponseShape.Encoders.Rights
import ResponseShape.Encoders.SpeechActs
import ResponseShape.Encoders.Reports
import ResponseShape.Encoders.Risk
import ResponseShape.Encoders.RiskEval
import ResponseShape.Encoders.Quantity
import ResponseShape.Encoders.Discourse
import ResponseShape.Encoders.ReadingsRoute

/-! # Every encoder against its shape

For every mode of the service (every constructor of `VE.Service.Mode`, so a new mode fails the
build until it is proved), every row its runner returns fits the skeleton of the mode's row
shape (`ResponseShape.Skeletons.row`, extracted from `ResponseShape.Schemas`): each object the
runner builds has exactly the fields the shape allows, every field the shape requires, none it
forbids, and a field the shape ties to another field's value exactly with that value. A field an
encoder adds or drops, or a shape that lists another field, fails the build until the two agree.
The proofs are per mode in `ResponseShape.Encoders.*`; values the runners copy from the request
are marked in the shapes (`Shape.copied`). -/

namespace ResponseShape.Encoders
open Lean ResponseShape ResponseShape.Skeletons

theorem runMode_fits (m : VE.Service.Mode) (j : Json) : Fits Γ (row m) (VE.Service.runMode m j) := by
  cases m
  · exact Conformance.evaluate_fits j
  · exact Conformance.checkCertificate_fits j
  · exact Conformance.order_fits j
  · exact Route.runCaseReported_fits j
  · exact Norms.runCaseReported_fits j
  · exact English.english_fits j
  · exact Standalone.environment_reported j
  · exact Standalone.model_reported j
  · exact Standalone.check_reported j
  · exact Standalone.identity_reported j
  · exact Standalone.parse_reported j
  · exact Family.graph_reported j
  · exact Family.readings_reported j
  · exact Family.bundle_reported j
  · exact Family.familyNorms_reported j
  · exact SoftNorms.runCaseReported_fits j
  · exact Rights.runCaseReported_fits j
  · exact SpeechActs.runCaseReported_fits j
  · exact Reports.runCaseReported_fits j
  · exact Alternatives.runCaseReported_fits j
  · exact Risk.runCaseReported_fits j
  · exact RiskEval.runCaseReported_fits j
  · exact Quantity.runCaseReported_fits j
  · exact NormDefaults.runCaseReported_fits j
  · exact Discourse.runCaseReported_fits j
  · exact ReadingsRoute.runCaseReported_fits j
  · exact English.diagnose_fits j

end ResponseShape.Encoders
