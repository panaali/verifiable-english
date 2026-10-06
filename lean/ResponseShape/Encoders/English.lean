import ResponseShape.Encoders.Common

/-! The `english` mode (`Service.englishReported`, the English runner) against `english.json#/row`,
and the `diagnose` mode (`Service.Diagnose.diagnoseCase`) against `diagnose.json#/row`. -/

namespace ResponseShape.Encoders.English
open Lean ResponseShape ResponseShape.Skeletons
open VE.English.ServiceRun

variable {req : Json}

theorem runCase_fits (E : VE.Environment) (L : VE.English.Lexicon) (j : Json) :
    OkFits req (skel% "english.json#/$defs/item") (runCase E L j) := by
  unfold runCase
  okfits
  fits

theorem run_fits (input : String) : OkFits req Skeletons.english (run input) := by
  unfold run
  okfits
  fits
  exact Fits.arrOf (OkP.arrayMapM (fun c _ => runCase_fits _ _ c) _ ‹_›)

theorem reported_fits (raw : String) : Fits req Skeletons.english (match run raw with
    | .ok result => result
    | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)]) := by
  split
  · exact run_fits _ _ ‹_›
  · fits

theorem english_fits (j : Json) : Fits j Skeletons.english (VE.Service.englishReported j) :=
  reported_fits _

theorem diagnose_fits (j : Json) : Fits j Skeletons.diagnose (VE.Service.Diagnose.diagnoseCase j) := by
  unfold VE.Service.Diagnose.diagnoseCase VE.WireContract.Diagnose.diagnoseCase VE.WireContract.record
  simp only []
  fits

end ResponseShape.Encoders.English
