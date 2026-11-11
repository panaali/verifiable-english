import ResponseShape

/-! The source of `ve/backends/lean_service_schema/clauses-elaborate.json` (`file`; `tools/response_schemas.py` writes
it): the `clauses-elaborate` mode's row (`VE.RightClauses.Run.runCaseReported`, docs/spec/right-clauses.md 8.1): the
plained document's canonical bytes, the slot `clauseSlotLabelled` (each premise its label and generated formula), and
the elided bytes (6): the document total and one count per unit of the request's document, in its order; and, when
the request carries `english`, the shown lines of spec 2 (frame, rule name, text; cmp-s3-cfr-1d). The relay that
binds them to the request is cmp-s3-cfr-1b's. -/
namespace ResponseShape.Schemas.ClausesElaborate
open Lean ResponseShape

def result : Shape :=
  c "VE.RightClauses.Run.elaborateCase: the plained document's canonical bytes, clauseSlotLabelled, the elided bytes and the shown RC lines." [
    obj, .required ["plained", "clause_slot", "elided_bytes", "unit_elided_bytes"],
    closed [("plained", ref "common.json#/$defs/text"),
      ("elided_bytes", ref "common.json#/$defs/nat"),
      ("unit_elided_bytes", n [arr, .items (ref "common.json#/$defs/nat"), .length "/document"]),
      ("clause_slot", n [arr, .items (n [obj, .required ["label", "ast"],
        closed [("label", ref "common.json#/$defs/text"), ("ast", ref "common.json#/$defs/generated_formula")]])]),
      ("english", n [arr, .items (n [obj, .required ["frame", "rule", "text"],
        closed [("frame", ref "common.json#/$defs/text"), ("rule", ref "common.json#/$defs/text"),
          ("text", ref "common.json#/$defs/text")]])])]]

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
