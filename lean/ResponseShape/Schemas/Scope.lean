import ResponseShape
import VE.Scope.Run

/-! The source of `ve/backends/lean_service_schema/scope.json` (`file`; `tools/response_schemas.py` writes it): the
`scope` mode's row (`VE.Scope.Run.runCaseReported`, docs/spec/scope.md 5.3). An answer has one row per governed unit,
each with its contributing governors and each governor's provenance sentence, and the block's governors in order with
the units whose rows list them. The ids and units are the request document's: the relay binds them to it
(`ve.scope.answer_problem`), since the request carries the document as text. -/
namespace ResponseShape.Schemas.Scope
open Lean ResponseShape

def governor : Shape :=
  c "VE.Scope.Run.govJson: a contributing governor's id, unit, effect word, reach and provenance sentence." [
    obj, .required ["id", "unit", "effect", "reach", "provenance"],
    closed [("id", str), ("unit", str), ("effect", enumS VE.Scope.effectWords), ("reach", n [arr, .items str]),
      ("provenance", str)]]

def unitRow : Shape :=
  c "VE.Scope.Run.rowJson: a governed unit and its contributing governors." [
    obj, .required ["unit", "governors"],
    closed [("unit", str), ("governors", n [arr, .minItems 1, .items (ref "#/$defs/governor")])]]

def governed : Shape :=
  c "VE.Scope.Run.governedJson: a governor of the block, in its order, and the units whose rows list it." [
    obj, .required ["id", "units"], closed [("id", str), ("units", n [arr, .items str])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "rows", "governed"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"),
        ("rows", n [arr, .items (ref "#/$defs/unit_row")]), ("governed", n [arr, .items (ref "#/$defs/governed")])]]]

def file : File where
  name := "scope.json"
  comment := some "Mode scope: VE.Scope.Run.runCaseReported. Each governed unit's governors and provenance sentences."
  top := [("row", «row»)]
  defs := [("governor", .schema governor), ("unit_row", .schema unitRow), ("governed", .schema governed)]

end ResponseShape.Schemas.Scope
