import ResponseShape.DefaultsExamples
import VE.Service.CoreCheckExamples

/-! The core rows of `document.json` (kb-2a-b: `core_view`, `core_row`, `core_statement`, `core_choices`,
`core_statements` and the `lowering` mark of a refusal) on the mode's own answers to the fixtures of
`VE/Service/CoreCheckExamples.lean`: each answer and refusal is accepted, and an answer with a member added, dropped or
retyped in its view's units, choices or statements, or in a row's answer, is refused. -/
namespace ResponseShape.CoreCheckExamples
open Lean VE.Service.CoreCheckExamples
open ResponseShape.DefaultsExamples (variants)

def case (f : String) : Json :=
  Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++ f ++ "\n---\n" ++ body)), ("admit", .bool true)]
def accepts (j a : Json) : Bool := (ResponseShape.decide Schemas.files (.ref "document.json#/row") { value := j } a).toOption.isSome
def answer : Json := VE.Service.CoreCheck.runCaseReported (case front)

/-- The answer with the member at `path` (object keys and array indexes) replaced by `v`. -/
def setAt : List (Sum String Nat) → Json → Json → Json
  | [], _, v => v
  | .inl k :: rest, j, v => j.setObjVal! k (setAt rest (j.getObjValD k) v)
  | .inr i :: rest, .arr xs, v => .arr (xs.set! i (setAt rest xs[i]! v))
  | _ :: _, j, _ => j
def getAt : List (Sum String Nat) → Json → Json
  | [], j => j
  | .inl k :: rest, j => getAt rest (j.getObjValD k)
  | .inr i :: rest, .arr xs => getAt rest xs[i]!
  | _ :: _, _ => .null

/-- Every variant of the member at `path`, the members in `optional` kept. -/
def refusedAt (path : List (Sum String Nat)) (optional : List String) : Bool :=
  (variants optional 5 (getAt path answer)).all fun w => !accepts (case front) (setAt path answer w)

-- accepted: the answer and the refusals (marked, and unmarked on today's path)
#guard accepts (case front) answer
#guard [front.replace "\"unit\":\"u4\"" "\"unit\":\"u9\"", front.replace "\"name\":\"h\"" "\"name\":\"h\",\"rank\":\"nowhere\"",
  front.replace "\"format\":\"ve-document@1\"" "\"format\":\"ve-document@1\",\"couplings\":[]"].all fun f =>
    let a := VE.Service.CoreCheck.runCaseReported (case f)
    a.getObjValD "status" == .str "error" && accepts (case f) a
-- refused: the mark other than true, and any member added, dropped or retyped
#guard !accepts (case front) (Json.mkObj [("id", .str "d"), ("status", .str "error"), ("error", .str "x"), ("lowering", .bool false)])
#guard refusedAt [.inl "view", .inl "choices"] []
#guard refusedAt [.inl "view", .inl "statements"] ["reading"]
#guard refusedAt [.inl "view", .inl "units", .inr 3] ["parent_id", "content", "meaning_id"]
#guard (List.range 2).all fun i => refusedAt [.inl "rows", .inr i, .inl "answer"] []
#guard !accepts (case front) (answer.setObjVal! "extra" .null) && !accepts (case front) (answer.setObjVal! "rows" (Json.arr #[]))

end ResponseShape.CoreCheckExamples
