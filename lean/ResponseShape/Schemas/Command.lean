import ResponseShape

/-! The source of `ve/backends/lean_service_schema/english.command.json` (`file`; `tools/response_schemas.py` writes
it): the `english.command` mode's row (`VE.Commands.Run.caseReported`, docs/spec/commands-imperatives.md section 6).
The relay binds the id, unit, wording, each fill's constant, words and span, the act and the query to its request;
the guard, paraphrase, legend, code, class and text are Lean's. -/
namespace ResponseShape.Schemas.Command
open Lean ResponseShape

def fill : Shape :=
  c "VE.Commands.Run.readingJson: a fill's constant and words, and their span in code points of the wording (null for the proof task's query)." [
    obj, .required ["constant", "words", "span"],
    closed [("constant", str), ("words", str), ("span", .anyOf [n [.type ["null"]],
      n [arr, .prefixItems [ref "common.json#/$defs/nat", ref "common.json#/$defs/nat"], .minItems 2, .maxItems 2]])]]

def reading : Shape :=
  c "VE.Commands.Run.readingJson: the command object (SA 3.2), its fills, the proof task's query (else null) and speech-acts' paraphrase." [
    obj, .required ["command", "fills", "query", "paraphrase"],
    closed [
      ("command", n [obj, .required ["force", "act", "args", "guard"],
        closed [("force", enumS ["require", "forbid"]), ("act", str), ("args", ref "common.json#/$defs/strings"),
          ("guard", ref "common.json#/$defs/generated_formula")]]),
      ("fills", n [arr, .items (ref "#/$defs/fill")]),
      ("query", .anyOf [n [.type ["null"]], str]),
      ("paraphrase", ref "common.json#/$defs/text")]]

def answer : Shape :=
  let base : List (String × Shape) := [("unit", str), ("wording", str), ("legend", ref "common.json#/$defs/strings")]
  let base_keys := ["unit", "wording", "legend", "outcome"]
  .anyOf [
    c "readInstruction's one reading." [obj, .required (base_keys ++ ["reading"]),
      closed (base ++ [("outcome", constS "one"), ("reading", ref "#/$defs/reading")])],
    c "readInstruction's readings (2 to readingsBound)." [obj, .required (base_keys ++ ["readings"]),
      closed (base ++ [("outcome", constS "many"), ("readings", n [arr, .items (ref "#/$defs/reading")])])],
    c "readInstruction's refusal: its code, class and text (QueryMismatch's text is the unit)." [obj,
      .required (base_keys ++ ["code", "class", "text"]),
      closed (base ++ [("outcome", constS "refused"), ("code", str), ("class", str), ("text", str)])],
    c "readInstruction at its work limit (Texts.limitText)." [obj, .required (base_keys ++ ["text"]),
      closed (base ++ [("outcome", constS "limit"), ("text", ref "common.json#/$defs/text")])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", str), ("status", constS "ok"), ("result", ref "#/$defs/answer")]]]

def file : File where
  name := "english.command.json"
  comment := some "Mode english.command: VE.Commands.Run.caseReported. readInstruction's outcome for one command wording."
  top := [("row", «row»)]
  defs := [("fill", .schema fill), ("reading", .schema reading), ("answer", .schema answer)]

end ResponseShape.Schemas.Command
