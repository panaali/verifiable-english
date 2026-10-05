import ResponseShape.FitsTactic
import VE.Service.Protocol

/-! Encoders several modes share: the claims and reports of an admission (`Route.Run.claimJson`,
`Norms.Run.reportJson`). -/

namespace ResponseShape.Encoders.Common
open Lean ResponseShape ResponseShape.Skeletons

theorem claimJson_fits (c : VE.Graph.Claim) :
    Fits Γ (skel% "common.json#/$defs/claim") (VE.Route.Run.claimJson c) := by
  unfold VE.Route.Run.claimJson
  fits

theorem reportJson_fits (r : VE.Graph.Report) :
    Fits Γ (skel% "common.json#/$defs/bound_report") (VE.Norms.Run.reportJson r) := by
  unfold VE.Norms.Run.reportJson
  fits
  all_goals exact claimJson_fits _

end ResponseShape.Encoders.Common
