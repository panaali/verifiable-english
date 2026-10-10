import ResponseShape

/-! The `english.question` row (docs/spec/question-answering.md 4.1 and 8). As for E2's English modes, the
result is not described here: the relay checks every field of it against the contract the mode exports
(`{"id", "export": "codes"}`: codes, classes, status codes and the fields of each status), which is the
producer's own table, and against the request's identities. -/
namespace ResponseShape.Schemas.Question
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .bool true), ("status", constS "error"), ("error", str)]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", .bool true), ("status", constS "ok"), ("result", .bool true)]]]

def file : File where
  name := "english.question.json"
  comment := some "Lean question reading response."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.Question
