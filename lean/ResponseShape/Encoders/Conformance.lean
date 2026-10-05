import ResponseShape.Encoders.Common

/-! The `ve_conformance` modes: `evaluate` (`Order.runEvaluationCaseReported`),
`check-certificate` (`CertificateWire.runCaseReported`) and `order` (`Order.Surface.runCaseReported`)
against their row shapes. -/

namespace ResponseShape.Encoders.Conformance
open Lean ResponseShape ResponseShape.Skeletons

theorem evaluationCase_fits (j : Json) : OkFits Γ Skeletons.evaluate (VE.Order.runEvaluationCase j) := by
  unfold VE.Order.runEvaluationCase VE.Closure.Bridge.runCase VE.Bridge.runCase
  okfits
  all_goals fits

theorem evaluate_fits (j : Json) : Fits Γ Skeletons.evaluate (VE.Order.runEvaluationCaseReported j) := by
  unfold VE.Order.runEvaluationCaseReported
  split
  · exact evaluationCase_fits j _ ‹_›
  · fits

theorem certificateCase_fits (j : Json) :
    OkFits Γ Skeletons.checkCertificate (VE.CertificateWire.runCase j) := by
  unfold VE.CertificateWire.runCase VE.CertificateWire.runClosureCase
  okfits
  all_goals fits

theorem checkCertificate_fits (j : Json) :
    Fits Γ Skeletons.checkCertificate (VE.CertificateWire.runCaseReported j) := by
  unfold VE.CertificateWire.runCaseReported
  split
  · exact certificateCase_fits j _ ‹_›
  · fits

theorem orderCase_fits (j : Json) : OkFits Γ Skeletons.order (VE.Order.Surface.runCase j) := by
  unfold VE.Order.Surface.runCase VE.Order.Wire.runCase
  okfits
  all_goals fits

theorem order_fits (j : Json) : Fits Γ Skeletons.order (VE.Order.Surface.runCaseReported j) := by
  unfold VE.Order.Surface.runCaseReported
  split
  · exact orderCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Conformance
