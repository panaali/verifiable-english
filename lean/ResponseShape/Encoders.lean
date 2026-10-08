import ResponseShape.Encoders.Conformance
import ResponseShape.Encoders.English
import ResponseShape.Encoders.EnglishLean
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
import ResponseShape.Encoders.Envelope

/-! # Every encoder against its shape

For every mode of the service (every constructor of `VE.Service.Mode`, so a new mode fails the
build until it is proved), every row its runner returns for a case fits the skeleton of the
mode's row shape (`ResponseShape.Skeletons.row`, extracted from `ResponseShape.Schemas`): each
object the runner builds has exactly the fields the shape allows, every field the shape
requires, none it forbids, and a field the shape ties to another field's value, or to the case,
exactly when the shape has it. The case is one the service decodes (`CaseWF`: its object map is
well formed), which the readings-route mode needs to read the case's kind through its rewrite. A field an
encoder adds or drops, or a shape that lists another field, fails the build until the two agree.
The proofs are per mode in `ResponseShape.Encoders.*`; values the runners copy from the request
are marked in the shapes (`Shape.copied`). The service's own lines (each result bound to its
position and case digest, the response, a request error) are proved against `envelope.json` in
`ResponseShape.Encoders.Envelope`. -/

namespace ResponseShape.Encoders
open Lean ResponseShape ResponseShape.Skeletons

variable {req : Json}

theorem runMode_fits (m : VE.Service.Mode) (j : Json) (hj : CaseWF j) : Fits j (row m) (VE.Service.runMode m j) := by
  cases m
  · exact Conformance.evaluate_fits j
  · exact Conformance.checkCertificate_fits j
  · exact Conformance.order_fits j
  · exact Route.runCaseReported_fits j
  · exact Norms.runCaseReported_fits j hj
  · exact English.english_fits j
  · exact EnglishLean.read_fits j
  · exact EnglishLean.grammar_fits j
  · exact EnglishLean.check_fits j
  · exact Standalone.environment_reported j
  · exact Standalone.model_reported j
  · exact Standalone.check_reported j
  · exact Standalone.identity_reported j
  · exact Standalone.parse_reported j
  · exact Family.graph_reported j
  · exact Family.readings_reported j
  · exact Family.bundle_reported j
  · exact Family.familyNorms_reported j
  · exact SoftNorms.runCaseReported_fits j hj
  · exact Rights.runCaseReported_fits j hj
  · exact SpeechActs.runCaseReported_fits j hj
  · exact Reports.runCaseReported_fits j
  · exact Alternatives.runCaseReported_fits j hj
  · exact Risk.runCaseReported_fits j hj
  · exact RiskEval.runCaseReported_fits j
  · exact Quantity.runCaseReported_fits j
  · exact NormDefaults.runCaseReported_fits j hj
  · exact Discourse.runCaseReported_fits j
  · exact ReadingsRoute.runCaseReported_fits j hj
  · exact English.diagnose_fits j

end ResponseShape.Encoders
