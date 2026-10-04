import VE.WireContract.Diagnose

/-! The `ve_service` mode `diagnose` (docs/LEAN-FIRST-PLAN.md, batch 1): glue over the
`ve_diagnose` runner. Like that runner it decides no verdict: it names the first failing
check of a wire contract (docs/spec/wire-contract.md 4.2). It is the one service module that
imports the diagnostic-only `VE.WireContract` (7.3); `VE.Service.Protocol` dispatches to it
from the `diagnose` mode alone, and every verdict mode is pinned to its own runner
(`runMode_*`). -/

namespace VE.Service.Diagnose
open Lean

/-- A `diagnose` case `{"unit", "case"}`: the row `ve_diagnose <unit>` prints for `case`
(`VE.WireContract.Diagnose.diagnoseCase`). A unit with no registered contract is an error row
with the one-shot runner's text, bound to the inner case's id. -/
def diagnoseCase (j : Json) : Json :=
  let inner := j.getObjValD "case"
  let error (message : String) : Json :=
    Json.mkObj [("id", inner.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  match j.getObjValD "unit" with
  | .str unit => match VE.WireContract.Diagnose.units.lookup unit with
    | some registered => VE.WireContract.Diagnose.diagnoseCase registered inner
    | none => error s!"UnsupportedProfile: no wire contract {unit}"
  | _ => error "InvalidInput: a diagnose case names its unit"

/-- `diagnose` on a registered unit is that unit's `ve_diagnose` row. -/
theorem diagnoseCase_registered (j : Json) (unit : String)
    (registered : VE.WireContract.Diagnose.Registered) (hu : j.getObjValD "unit" = .str unit)
    (hr : VE.WireContract.Diagnose.units.lookup unit = some registered) :
    diagnoseCase j = VE.WireContract.Diagnose.diagnoseCase registered (j.getObjValD "case") := by
  simp [diagnoseCase, hu, hr]

end VE.Service.Diagnose
