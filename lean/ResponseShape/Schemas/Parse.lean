import ResponseShape

/-! The source of `ve/backends/lean_service_schema/parse.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Parse
open Lean ResponseShape

def parse_error : Shape :=
  n [obj, .required ["id", "status", "error", "span"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "error"),
      ("error", ref "common.json#/$defs/text"),
      ("span", n [obj, .required ["start", "end", "line", "column"],
        closed [("start", ref "common.json#/$defs/nat"),
          ("end", ref "common.json#/$defs/nat"),
          ("line", ref "common.json#/$defs/nat"),
          ("column", ref "common.json#/$defs/nat")]])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    ref "#/$defs/parse_error",
    n [
      obj,
      .required ["id", "status", "ast"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("ast", n [arr, .minItems 1, .items (n [arr, .minItems 1])]),
        ("canonical", str)]]]

def file : File where
  name := "parse.json"
  comment := some "Standalone parse (Standalone.parseCase): the family's surface parser accepted and typed the source; the document on the wire and, where the family has a printer, its canonical text."
  top := [("row", «row»)]
  defs := [("parse_error", .schema parse_error)]

end ResponseShape.Schemas.Parse
