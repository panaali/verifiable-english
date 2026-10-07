import ResponseShape.Encoders.Common

/-! The `ve_conformance` modes: `evaluate` (`Order.runEvaluationCaseReported`),
`check-certificate` (the service's metered `CertificateWire.runCaseReportedSteps`)
and `order` (`Order.Surface.runCaseReported`) against their row shapes. -/

namespace ResponseShape.Encoders.Conformance
open Lean ResponseShape ResponseShape.Skeletons

variable {req : Json}

/-- A countermodel case has the kind `countermodel`; every other is a document (no kind). -/
theorem evaluationCase_fits (j : Json) : OkFits j Skeletons.evaluate (VE.Order.runEvaluationCase j) := by
  unfold VE.Order.runEvaluationCase VE.Closure.Bridge.runCase VE.Bridge.runCase
  okfits
  all_goals first
    | have := Common.kind_holds_of_val ‹j.getObjVal? "kind" = .ok _› ‹(_ == some "countermodel") = true›
    | have := Common.lacks_of_none ‹j.getObjVal? "environment" = .ok _› ‹∀ _, j.getObjVal? "kind" = .ok _ → False›
  all_goals fits

theorem evaluate_fits (j : Json) : Fits j Skeletons.evaluate (VE.Order.runEvaluationCaseReported j) := by
  unfold VE.Order.runEvaluationCaseReported
  split
  · exact evaluationCase_fits j _ ‹_›
  · fits

theorem certificateCase_fits (j : Json) :
    OkFits req Skeletons.checkCertificate (VE.CertificateWire.runCase j) := by
  unfold VE.CertificateWire.runCase VE.CertificateWire.runClosureCase
  okfits
  all_goals fits

theorem checkCertificate_fits (j : Json) :
    Fits req Skeletons.checkCertificate (VE.CertificateWire.runCaseReportedSteps j) := by
  unfold VE.CertificateWire.runCaseReportedSteps
  split
  · exact certificateCase_fits j _ ‹_›
  · fits

/-- The kind is required: `Surface.runCase` reads it as a string (`surface`, or else `Wire.runCase`'s). -/
theorem orderCase_fits (j : Json) : OkFits j Skeletons.order (VE.Order.Surface.runCase j) := by
  unfold VE.Order.Surface.runCase VE.Order.Wire.runCase
  okfits
  all_goals first
    | have hK := Common.getObjValD_of_stringField ‹VE.Bridge.stringField j "kind" = .ok _›
    | (have hK := Common.getObjValD_of_as ‹j.getObjValAs? String "kind" = .ok _›
       obtain rfl : _ = "surface" := by simpa using ‹¬(_ != "surface") = true›)
  all_goals kind_subst
  all_goals fits

theorem order_fits (j : Json) : Fits j Skeletons.order (VE.Order.Surface.runCaseReported j) := by
  unfold VE.Order.Surface.runCaseReported
  split
  · exact orderCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Conformance
