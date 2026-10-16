import ResponseShape

/-! The source of `ve/backends/lean_service_schema/parse.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Parse
open Lean ResponseShape

/- The four standalone surface families encode to the same tagged document
grammar. This is the union of their term and formula constructors; family
typing remains the service's decision. -/
def term : Shape :=
  .tagged [
    ("var", [ref "common.json#/$defs/nat"]),
    ("const", [str]),
    ("num", [ref "common.json#/$defs/integer_text"]),
    ("add", [ref "#/$defs/term", ref "#/$defs/term"]),
    ("scale", [ref "common.json#/$defs/integer_text", ref "#/$defs/term"])]

def edge : Shape :=
  .tagged [
    ("named", [str]),
    ("body", [str, ref "#/$defs/formula"])]

def formula : Shape :=
  .tagged [
    ("top", []), ("bottom", []),
    ("unary", [str, ref "#/$defs/term"]),
    ("binary", [str, ref "#/$defs/term", ref "#/$defs/term"]),
    ("atom", [str, n [arr, .minItems 3, .maxItems 6, .items (ref "#/$defs/term")]]),
    ("eq", [ref "#/$defs/term", ref "#/$defs/term"]),
    ("lt", [ref "#/$defs/term", ref "#/$defs/term"]),
    ("le", [ref "#/$defs/term", ref "#/$defs/term"]),
    ("not", [ref "#/$defs/formula"]),
    ("and", [ref "#/$defs/formula", ref "#/$defs/formula"]),
    ("or", [ref "#/$defs/formula", ref "#/$defs/formula"]),
    ("implies", [ref "#/$defs/formula", ref "#/$defs/formula"]),
    ("forall", [str, ref "#/$defs/formula"]),
    ("exists", [str, ref "#/$defs/formula"]),
    ("reach", [enumS ["plus", "star"], ref "#/$defs/edge", ref "#/$defs/term", ref "#/$defs/term"])]

def parse_error : Shape :=
  n [obj, .required ["id", "status", "error", "span"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "error"),
      ("error", ref "common.json#/$defs/text"),
      ("span", n [obj, .required ["start", "end", "line", "column"],
        closed [("start", ref "common.json#/$defs/nat"),
          ("end", ref "common.json#/$defs/nat"),
          ("line", ref "common.json#/$defs/nat"),
          ("column", ref "common.json#/$defs/nat")],
        .sourceSpan "/source"])]]

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
        ("ast", n [arr, .minItems 1, .items (ref "#/$defs/formula")]),
        ("canonical", str)]]]

def file : File where
  name := "parse.json"
  comment := some "Standalone parse (Standalone.parseCase): the family's surface parser accepted and typed the source; the document on the wire and, where the family has a printer, its canonical text."
  top := [("row", «row»)]
  defs := [("parse_error", .schema parse_error), ("term", .schema term),
    ("edge", .schema edge), ("formula", .schema formula)]

end ResponseShape.Schemas.Parse
