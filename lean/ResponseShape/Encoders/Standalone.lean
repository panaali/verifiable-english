import ResponseShape.Encoders.Common

/-! The standalone modes (`Service.Standalone.reported` of `environmentCase`, `modelCase`,
`checkCase`, `identityCase`, `parseCase`) against their row shapes. -/

namespace ResponseShape.Encoders.Standalone
open Lean ResponseShape ResponseShape.Skeletons
open VE.Service.Standalone

variable {req : Json}

/-- The family an environment row names (`Gate.Family.name`, `Legacy.family`) is one of the schema's. -/
theorem family_fits (f : VE.Route.Gate.Family) :
    Fits req (.strIn ["fol", "closure", "closure+n-ary", "order"]) (.str f.name) := by
  cases f <;> fits

theorem legacy_family_fits (l : Legacy) :
    Fits req (.strIn ["fol", "closure", "closure+n-ary", "order"]) (.str l.family) := by
  cases l <;> simp only [Legacy.family] <;> fits

theorem environment_fits (j : Json) : OkFits req Skeletons.environment (environmentCase j) := by
  unfold environmentCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok, Legacy.family])
  all_goals fits using family_fits, legacy_family_fits

theorem model_fits (j : Json) : OkFits req Skeletons.model (modelCase j) := by
  unfold modelCase legacyModelCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem check_fits (j : Json) : OkFits req Skeletons.check (checkCase j) := by
  unfold checkCase legacyCheckCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem identity_fits (j : Json) : OkFits req Skeletons.identity (identityCase j) := by
  unfold identityCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  -- The kind the row echoes is the one the runner tested.
  all_goals (try kind_subst)
  all_goals fits

theorem parse_fits (j : Json) : OkFits req Skeletons.parse (parseCase j) := by
  unfold parseCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem environment_case_reported (j : Json) :
    Fits j Skeletons.environment (reported environmentCase j) := by
  unfold reported; split
  · exact environment_fits j _ ‹_›
  · fits

theorem model_case_reported (j : Json) :
    Fits j Skeletons.model (reported modelCase j) := by
  unfold reported; split
  · exact model_fits j _ ‹_›
  · fits

theorem environment_fault_fits (j : Json) (fault : ModelFault) :
    Fits j Skeletons.environment (reportedFault j fault) := by
  unfold reportedFault
  dsimp
  split <;> fits

theorem environment_with_path_fits (j result : Json) (fault : ModelFault)
    (h : Fits j Skeletons.environment result) :
    Fits j Skeletons.environment (withVocabularyPath j result fault) := by
  unfold withVocabularyPath
  repeat first
    | exact h
    | exact environment_fault_fits j _
    | split

theorem model_fault_fits (j : Json) (fault : ModelFault) :
    Fits j Skeletons.model (reportedFault j fault) := by
  unfold reportedFault
  dsimp
  split <;> fits

theorem legacy_environment_fits (j environment : Json) :
    Fits j Skeletons.environment (reportedLegacyEnvironment j environment) := by
  unfold reportedLegacyEnvironment
  split
  · exact environment_case_reported j
  · split
    · split
      · exact environment_fault_fits j _
      · exact environment_with_path_fits j _ _ (environment_case_reported j)
    · exact environment_case_reported j

theorem other_environment_fits (j environment : Json) :
    Fits j Skeletons.environment (reportedOtherEnvironment j environment) := by
  unfold reportedOtherEnvironment
  split
  · exact environment_case_reported j
  · exact legacy_environment_fits j environment

theorem environment_reported (j : Json) : Fits j Skeletons.environment (reportedEnvironment j) := by
  unfold reportedEnvironment
  split
  · exact environment_case_reported j
  · split
    · split
      · split
        · split
          · exact environment_fault_fits j _
          · exact environment_with_path_fits j _ _ (environment_case_reported j)
        · exact environment_case_reported j
      · exact other_environment_fits j _
    · split
      · exact environment_fault_fits j _
      · split
        · exact environment_case_reported j
        · exact environment_fault_fits j _

theorem model_reported (j : Json) : Fits j Skeletons.model (reportedModel j) := by
  unfold reportedModel
  dsimp only [Except.bind, Except.pure]
  repeat first
    | exact model_case_reported j
    | exact model_fault_fits j _
    | split

theorem check_reported (j : Json) : Fits j Skeletons.check (reported checkCase j) := by
  unfold reported; split
  · exact check_fits j _ ‹_›
  · fits

theorem identity_reported (j : Json) : Fits j Skeletons.identity (reported identityCase j) := by
  unfold reported; split
  · exact identity_fits j _ ‹_›
  · fits

theorem parse_reported (j : Json) : Fits j Skeletons.parse (reportedParse j) := by
  unfold reportedParse; split
  · exact parse_fits j _ ‹_›
  · split
    · unfold VE.Service.ParseDiagnostic.span
      fits
    · fits

end ResponseShape.Encoders.Standalone
