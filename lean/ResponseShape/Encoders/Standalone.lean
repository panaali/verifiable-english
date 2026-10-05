import ResponseShape.Encoders.Common

/-! The standalone modes (`Service.Standalone.reported` of `environmentCase`, `modelCase`,
`checkCase`, `identityCase`, `parseCase`) against their row shapes. -/

namespace ResponseShape.Encoders.Standalone
open Lean ResponseShape ResponseShape.Skeletons
open VE.Service.Standalone

theorem environment_fits (j : Json) : OkFits Γ Skeletons.environment (environmentCase j) := by
  unfold environmentCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem model_fits (j : Json) : OkFits Γ Skeletons.model (modelCase j) := by
  unfold modelCase legacyModelCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem check_fits (j : Json) : OkFits Γ Skeletons.check (checkCase j) := by
  unfold checkCase legacyCheckCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem identity_fits (j : Json) : OkFits Γ Skeletons.identity (identityCase j) := by
  unfold identityCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem parse_fits (j : Json) : OkFits Γ Skeletons.parse (parseCase j) := by
  unfold parseCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem environment_reported (j : Json) : Fits Γ Skeletons.environment (reported environmentCase j) := by
  unfold reported; split
  · exact environment_fits j _ ‹_›
  · fits

theorem model_reported (j : Json) : Fits Γ Skeletons.model (reported modelCase j) := by
  unfold reported; split
  · exact model_fits j _ ‹_›
  · fits

theorem check_reported (j : Json) : Fits Γ Skeletons.check (reported checkCase j) := by
  unfold reported; split
  · exact check_fits j _ ‹_›
  · fits

theorem identity_reported (j : Json) : Fits Γ Skeletons.identity (reported identityCase j) := by
  unfold reported; split
  · exact identity_fits j _ ‹_›
  · fits

theorem parse_reported (j : Json) : Fits Γ Skeletons.parse (reported parseCase j) := by
  unfold reported; split
  · exact parse_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Standalone
