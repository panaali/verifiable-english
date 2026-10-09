import ResponseShape

/-! The `english.question` row (docs/spec/question-answering.md 4.1 and 8). The result is an object with a
status of 4.1 and the question's identities; the fields of each status are the relay's to check against the
contract the mode exports (`{"id", "export": "codes"}`), which is also a result. -/
namespace ResponseShape.Schemas.Question
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .bool true), ("status", constS "error"), ("error", str)]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", .bool true), ("status", constS "ok"), ("result", obj)]]]

def file : File where
  name := "english.question.json"
  comment := some "Lean question reading response."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Question
