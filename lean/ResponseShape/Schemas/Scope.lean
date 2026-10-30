import ResponseShape
import VE.Scope.Run

/-! The source of `ve/backends/lean_service_schema/scope.json` (`file`; `tools/response_schemas.py` writes it): the
`scope` mode's row (`VE.Scope.Run.runCaseReported`, docs/spec/scope.md 5.3). An answer has one row per governed unit,
each with its contributing governors and one provenance sentence per governor. The ids and units are the request
document's: the relay binds them to it (`ve.scope.answer_problem`), since the request carries the document as text. -/
namespace ResponseShape.Schemas.Scope
open Lean ResponseShape

def governor : Shape :=
  c "VE.Scope.Run.govJson: a contributing governor's id, unit, effect word and reach." [
    obj, .required ["id", "unit", "effect", "reach"],
    closed [("id", str), ("unit", str), ("effect", enumS VE.Scope.effectWords), ("reach", n [arr, .items str])]]

def unitRow : Shape :=
  c "VE.Scope.Run.rowJson: a governed unit, its governors and one sentence per governor." [
    obj, .required ["unit", "governors", "provenance"], .sameLength ["governors", "provenance"],
    closed [("unit", str), ("governors", n [arr, .minItems 1, .items (ref "#/$defs/governor")]),
      ("provenance", n [arr, .minItems 1, .items str])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "rows"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"),
        ("rows", n [arr, .items (ref "#/$defs/unit_row")])]]]

def file : File where
  name := "scope.json"
  comment := some "Mode scope: VE.Scope.Run.runCaseReported. Each governed unit's governors and provenance sentences."
  top := [("row", «row»)]
  defs := [("governor", .schema governor), ("unit_row", .schema unitRow)]

end ResponseShape.Schemas.Scope
