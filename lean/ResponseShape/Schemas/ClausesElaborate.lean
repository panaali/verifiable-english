import ResponseShape

/-! The source of `ve/backends/lean_service_schema/clauses-elaborate.json` (`file`; `tools/response_schemas.py` writes
it): the `clauses-elaborate` mode's row (`VE.RightClauses.Run.runCaseReported`, docs/spec/right-clauses.md 8.1): the
plained document's canonical bytes and the slot `clauseSlotLabelled`, each premise its label and generated formula.
The relay that binds them to the request is cmp-s3-cfr-1b's. -/
namespace ResponseShape.Schemas.ClausesElaborate
open Lean ResponseShape

def result : Shape :=
  c "VE.RightClauses.Run.elaborateCase: the plained document's canonical bytes and clauseSlotLabelled." [
    obj, .required ["plained", "clause_slot"],
    closed [("plained", ref "common.json#/$defs/text"),
      ("clause_slot", n [arr, .items (n [obj, .required ["label", "ast"],
        closed [("label", ref "common.json#/$defs/text"), ("ast", ref "common.json#/$defs/generated_formula")]])])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("result", ref "#/$defs/result")]]]

def file : File where
  name := "clauses-elaborate.json"
  comment := some "Lean's head of right-clauses@0 on one document: the plained document and its premise slot."
  top := [("row", «row»)]
  defs := [("result", .schema result)]

end ResponseShape.Schemas.ClausesElaborate
