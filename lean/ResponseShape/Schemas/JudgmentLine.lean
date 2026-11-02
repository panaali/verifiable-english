import ResponseShape
import VE.EnglishGrammar.JudgmentLines

/-! The source of `ve/backends/lean_service_schema/judgment-line.json` (`file`; `tools/response_schemas.py` writes it): the
`judgment-line` mode's row (`VE.EnglishGrammar.JudgmentLines.runCaseReported`, docs/spec/judgment-terms.md 9.1), a
declaration line with its W2 record and its predicate. The relay binds each name to the request's line (`ve.judgment_lines`). -/
namespace ResponseShape.Schemas.JudgmentLine
open Lean ResponseShape

def record : Shape :=
  let words := ref "common.json#/$defs/strings"
  let none := n [arr, .maxItems 0]
  c "VE.EnglishGrammar.JudgmentLines.recordJson: the W2 record of a parsed line, with no criteria, factors or precedents." [
    obj, .required ["name", "arguments", "decided_by", "necessary", "sufficient", "factors", "precedents", "jurisdiction",
      "version"],
    closed [("name", str), ("arguments", words), ("decided_by", str), ("necessary", none), ("sufficient", none),
      ("factors", none), ("precedents", none), ("jurisdiction", n [str, .equals "/jurisdiction"]), ("version", .const (toJson (1 : Nat)))]]

def predicate : Shape :=
  c "The predicate a declaration line declares: its name and its sorts." [
    obj, .required ["name", "arguments"], closed [("name", str), ("arguments", ref "common.json#/$defs/strings")]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"], closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "line", "record", "predicate"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("line", n [str, .equals "/line"]), ("record", ref "#/$defs/record"),
        ("predicate", ref "#/$defs/predicate")]]]

def file : File where
  name := "judgment-line.json"
  comment := some "Lean's reading of a judgment declaration line."
  top := [("row", «row»)]
  defs := [("record", .schema record), ("predicate", .schema predicate)]

end ResponseShape.Schemas.JudgmentLine
