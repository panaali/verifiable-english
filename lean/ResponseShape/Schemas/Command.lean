import ResponseShape

/-! The source of `ve/backends/lean_service_schema/english.command.json` (`file`; `tools/response_schemas.py` writes
it): the `english.command` mode's row (`VE.Commands.Run.caseReported`, docs/spec/commands-imperatives.md section 6).
The generated shape binds id, unit and wording to the request. Relay binding of fills, spans, act and query is
deferred to ci-2b; guard, paraphrase, legend, code, class and text are Lean's. -/
namespace ResponseShape.Schemas.Command
open Lean ResponseShape

def fill : Shape :=
  c "VE.Commands.Run.readingJson: a fill's constant and words, and their span in code points of the wording (null for the proof task's query)." [
    obj, .required ["constant", "words", "span"],
    closed [("constant", ref "common.json#/$defs/text"), ("words", ref "common.json#/$defs/text"), ("span", .anyOf [n [.type ["null"]],
      n [arr, .prefixItems [ref "common.json#/$defs/nat", ref "common.json#/$defs/nat"], .minItems 2, .maxItems 2]])]]

def reading : Shape :=
  c "VE.Commands.Run.readingJson: the command object (SA 3.2), its fills (at most one: a decoded environment's predicates have at most two argument sorts), the proof task's query (else null) and speech-acts' paraphrase." [
    obj, .required ["command", "fills", "query", "paraphrase"],
    closed [
      ("command", n [obj, .required ["force", "act", "args", "guard"],
        closed [("force", enumS ["require", "forbid"]), ("act", ref "common.json#/$defs/text"),
          ("args", n [arr, .items (ref "common.json#/$defs/text"), .maxItems 1]),
          ("guard", ref "common.json#/$defs/generated_formula")]]),
      ("fills", n [arr, .items (ref "#/$defs/fill"), .maxItems 1]),
      ("query", .anyOf [n [.type ["null"]], ref "common.json#/$defs/text"]),
      ("paraphrase", ref "common.json#/$defs/text")]]

def answer : Shape :=
  let text := ref "common.json#/$defs/text"
  let base : List (String × Shape) := [("unit", n [str, .equals "/unit"]), ("wording", n [str, .equals "/wording"]),
    ("legend", n [arr, .items text, .minItems 1])]
  let base_keys := ["unit", "wording", "legend", "outcome"]
  .anyOf [
    c "readInstruction's one reading." [obj, .required (base_keys ++ ["reading"]),
      closed (base ++ [("outcome", constS "one"), ("reading", ref "#/$defs/reading")])],
    c "readInstruction's readings (2 to readingsBound)." [obj, .required (base_keys ++ ["readings"]),
      closed (base ++ [("outcome", constS "many"), ("readings", n [arr, .items (ref "#/$defs/reading")])])],
    c "readInstruction's refusal: its code, class and text (QueryMismatch's text is the unit)." [obj,
      .required (base_keys ++ ["code", "class", "text"]),
      closed (base ++ [("outcome", constS "refused"), ("code", text), ("class", text), ("text", text)])],
    c "readInstruction at its work limit (Texts.limitText)." [obj, .required (base_keys ++ ["text"]),
      closed (base ++ [("outcome", constS "limit"), ("text", text)])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("result", ref "#/$defs/answer")]]]

def file : File where
  name := "english.command.json"
  comment := some "Mode english.command: VE.Commands.Run.caseReported. readInstruction's outcome for one command wording."
  top := [("row", «row»)]
  defs := [("fill", .schema fill), ("reading", .schema reading), ("answer", .schema answer)]

end ResponseShape.Schemas.Command
