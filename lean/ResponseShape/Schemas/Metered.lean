import ResponseShape

/-! The `metered` row (`VE.Route.MeteredRun.runCaseReported`, batch 15a's metered evaluator, a service
mode since lean-first batch 18): for an `evaluate-budgeted` case the document's three-valued status, its
value and count and, when the case asks for one, its explanation as preorder rows (`MeteredTrace.Row`);
for a `non-vacuity` case whether the candidate is suitable, its count and whether the budget ran out.
The client binds the alternative to the kind it sent. -/
namespace ResponseShape.Schemas.Metered
open Lean ResponseShape

def binding : Shape :=
  c "MeteredTrace.bindingJson: a local bound around a node, innermost first (its position is its de Bruijn index)." [
    obj,
    .required ["debruijn_index", "sort", "local_id"],
    closed [("debruijn_index", ref "common.json#/$defs/nat"), ("sort", str), ("local_id", str)]]

def node : Shape :=
  c "MeteredTrace.Row.json: one explanation node in preorder and the number of its children, whose subtrees follow it in order." [
    obj,
    .required ["kind", "value", "bindings", "detail", "children"],
    closed [
      ("kind", str),
      ("value", .type ["boolean", "null"]),
      ("bindings", n [arr, .items (ref "#/$defs/binding")]),
      ("detail", str),
      ("children", ref "common.json#/$defs/nat")]]

/-- One of the three document results: its status and value, as `Metered.scan` writes them. -/
def result (status : String) (value : Json) : Shape :=
  n [
    obj,
    .required ["status", "value", "evaluations", "explanation"],
    closed [
      ("status", constS status),
      ("value", .const value),
      ("evaluations", ref "common.json#/$defs/nat"),
      ("explanation", .anyOf [.type ["null"], n [arr, .minItems 1, .items (ref "#/$defs/node")]])]]

def evaluation : Shape :=
  c "Metered.resultFields and the explanation (null unless the case asks for a trace): a satisfied document is true, a violated one false, an exhausted budget has no value." [
    .anyOf [result "Satisfied" (.bool true), result "Violated" (.bool false), result "ResourceLimit" .null]]

def evaluated : Shape :=
  n [
    obj,
    .required ["id", "status", "evaluation"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("evaluation", ref "#/$defs/evaluation")]]

def nonVacuity : Shape :=
  c "MeteredRun.nonVacuityResult." [
    obj,
    .required ["id", "status", "suitable", "evaluations", "exhausted"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("suitable", .type ["boolean"]),
      ("evaluations", ref "common.json#/$defs/nat"),
      ("exhausted", .type ["boolean"])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    ref "#/$defs/evaluated",
    ref "#/$defs/non_vacuity"]

def file : File where
  name := "metered.json"
  comment := some "Mode metered: Route.MeteredRun.runCaseReported (evaluate-budgeted and non-vacuity cases)."
  top := [("row", «row»)]
  defs := [
    ("binding", .schema binding),
    ("node", .schema node),
    ("evaluation", .schema evaluation),
    ("evaluated", .schema evaluated),
    ("non_vacuity", .schema nonVacuity)]

end ResponseShape.Schemas.Metered
