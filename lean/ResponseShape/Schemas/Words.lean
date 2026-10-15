import ResponseShape
import VE.Words.Run

/-! The `words` row (plan Q2.4): Lean's lines for the readings and norm-defaults English, one per item of the request,
with the identities of the environment and lexicon they were worded in. The relay binds the identities to the request
and the line count to its items (`ve.words.answer_problem`). -/
namespace ResponseShape.Schemas.Words
open Lean ResponseShape

def result : Shape :=
  c "VE.Words.Run.wordsCase: the identities and one line per item." [
    obj, .required ["environment_id", "lexicon_id", "lines"],
    closed [("environment_id", str), ("lexicon_id", str), ("lines", n [arr, .items str])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"), ("result", ref "#/$defs/result")]]]

def file : File where
  name := "words.json"
  comment := some "Lean's situation lines, point clauses, filled-gap and pair sentences, one per requested item."
  top := [("row", «row»)]
  defs := [("result", .schema result)]

end ResponseShape.Schemas.Words
