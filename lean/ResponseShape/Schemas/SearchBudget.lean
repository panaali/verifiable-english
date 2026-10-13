import ResponseShape

/-! The `search-budget` row (`VE.SearchBudget.Run`): the premise check's budget and, for each sort
the request lists, its raised bounds `{"least", "most"}` or `null`, one entry per requested sort in
order (`x-zip`), so the answer names no sort the request does not. -/
namespace ResponseShape.Schemas.SearchBudget
open Lean ResponseShape

def bound : Shape :=
  .anyOf [
    .type ["null"],
    n [obj, .required ["least", "most"],
      closed [("least", ref "common.json#/$defs/nat"), ("most", ref "common.json#/$defs/nat")]]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [obj,
      .required ["id", "status", "max_proof_steps", "max_domain_size", "max_models", "max_evaluations", "sorts"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("max_proof_steps", ref "common.json#/$defs/nat"),
        ("max_domain_size", ref "common.json#/$defs/nat"),
        ("max_models", ref "common.json#/$defs/nat"),
        ("max_evaluations", ref "common.json#/$defs/nat"),
        ("sorts", n [.type ["array"], .zip "/sorts" (ref "#/$defs/bound")])]]]

def file : File where
  name := "search-budget.json"
  comment := some "Mode search-budget: SearchBudget.Run.runCaseReported, the premise check's search budget."
  top := [("row", «row»)]
  defs := [("bound", .schema bound)]

end ResponseShape.Schemas.SearchBudget
