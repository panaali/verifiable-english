import ResponseShape

/-! The source of `ve/backends/lean_service_schema/evaluate.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Evaluate
open Lean ResponseShape

def document : Shape :=
  c "That value is the conjunction of values is the service's." [
    obj,
    .required ["id", "status", "values", "value", "canonical"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("values", ref "common.json#/$defs/values"),
      ("value", .type ["boolean"]),
      ("canonical", str)]]

def countermodel : Shape :=
  n [
    obj,
    .required ["id", "status", "refutes"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("refutes", .type ["boolean"])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    .select [
      (ref "common.json#/$defs/no_kind", ref "#/$defs/document"),
      (kindIs "countermodel", ref "#/$defs/countermodel")]]

def file : File where
  name := "evaluate.json"
  comment := some "Mode evaluate: Order.runEvaluationCaseReported (Bridge.runCase, Closure.Bridge.runCase). A kind field selects a countermodel request and must be exactly countermodel."
  top := [("row", «row»)]
  defs := [
    ("document", .schema document),
    ("countermodel", .schema countermodel)]

end ResponseShape.Schemas.Evaluate
