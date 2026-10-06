import ResponseShape
import VE.Service.Protocol

/-! # The runners' tests of the request case

A mode whose answer depends on which runner takes the case (`SoftNorms.Run.usesSoftPath` and
the like) says so with an `x-select` whose condition is one of these tests: the shape's grammar
of the condition, decided beside it by the runner's own Lean function (a `lean` node, which the
client's validation and `ve_response_decode` must find in agreement). `decidedCase d s` is that
node, with the function of `d`; the skeletons (`ResponseShape.Skeleton`) keep it as the condition
`CaseCond.decided d`, which holds of a case exactly when the same function does, so the encoder
theorems tie each answer to the runner's own test. A schema names such a test only through
`decidedCase`, so the function the shape decides with and the one the skeleton reads are one. -/

namespace ResponseShape
open Lean

inductive CaseDecider where
  | softPath
  | rightsPath
  | normDefaultsPath
  | normsPath
  | discoursePath
  | altPath
  | riskPath
  | reportsPath
  | speechPath
  deriving Inhabited, Repr, BEq, DecidableEq, Lean.ToExpr

namespace CaseDecider

/-- Every decider (`all_complete`). -/
def all : List CaseDecider :=
  [.softPath, .rightsPath, .normDefaultsPath, .normsPath, .discoursePath, .altPath, .riskPath, .reportsPath,
    .speechPath]

theorem all_complete (d : CaseDecider) : d ∈ all := by
  cases d <;> simp [all]

/-- The Lean function the shape's condition names. -/
def name : CaseDecider → String
  | .softPath => "SoftNorms.Run.usesSoftPath"
  | .rightsPath => "Rights.Run.usesRightsPath"
  | .normDefaultsPath => "NormDefaults.Run.usesNormDefaultsPath"
  | .normsPath => "Norms.Run.usesNormsPath or Norms.Plain.layered"
  | .discoursePath => "Discourse.Run.usesDiscoursePath"
  | .altPath => "Alternatives.Run.usesAltPath"
  | .riskPath => "Risk.Run.usesRiskPath"
  | .reportsPath => "Reports.Run.usesReportsPath"
  | .speechPath => "SpeechActs.Run.usesSpeechPath"

/-- The runner's test of the case. -/
def fn : CaseDecider → Json → Bool
  | .softPath => VE.SoftNorms.Run.usesSoftPath
  | .rightsPath => VE.Rights.Run.usesRightsPath
  | .normDefaultsPath => VE.NormDefaults.Run.usesNormDefaultsPath
  | .normsPath => fun j => VE.Norms.Run.usesNormsPath j || VE.Norms.Plain.layered (j.getObjValD "environment")
  | .discoursePath => VE.Discourse.Run.usesDiscoursePath
  | .altPath => VE.Alternatives.Run.usesAltPath
  | .riskPath => VE.Risk.Run.usesRiskPath
  | .reportsPath => VE.Reports.Run.usesReportsPath
  | .speechPath => VE.SpeechActs.Run.usesSpeechPath

def ofName? (n : String) : Option CaseDecider := all.find? (·.name == n)

-- The names are distinct, so a name gives back its decider.
#guard all.all fun d => ofName? d.name == some d

end CaseDecider

/-- The shape `s` of a runner's test of the case, decided beside it by that test. -/
def decidedCase (d : CaseDecider) (s : Shape) : Shape := .lean d.name s d.fn

end ResponseShape
