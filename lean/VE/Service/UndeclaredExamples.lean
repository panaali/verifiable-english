import VE.Service.Document

/-! The document mode's `undeclared_evaluative` member (docs/spec/judgment-terms.md 7 and 8.4; jt-3a), on spec
11.7's predicates: `Env.basePredicates` reads every base predicate once with its words (its name, then its
`verbalisation`), a W3-defined name excluded and a regulated one kept, and `encode` writes the list under
`judgments@0` only. `tests/test_judgments_undeclared.py` checks the same answers through the service and the relay. -/

namespace VE.Service.UndeclaredExamples
open Lean VE.Service.Document

def act : Json := Json.mkObj [("arguments", toJson ["act"]), ("description", .str "an act")]

def vocabulary : Json := Json.mkObj [
  ("sorts", Json.mkObj [("person", Json.mkObj [("description", .str "a person")]),
    ("act", Json.mkObj [("description", .str "an act")])]),
  ("predicates", Json.mkObj [("reasonable_grounds", act), ("due_date", act), ("arbitrary", act), ("arrest", act),
    ("trial", act.setObjVal! "verbalisation" (.str "{0} is a fair trial")),
    ("reasonable_detention", act.setObjVal! "defined" (Json.mkObj [("arguments", toJson ["act"]),
      ("body", toJson [toJson "and", toJson [toJson "unary", toJson "arrest", toJson [toJson "var", toJson 0]],
        toJson [toJson "unary", toJson "arbitrary", toJson [toJson "var", toJson 0]]])])),
    ("make_reasonable_efforts", Json.mkObj [("arguments", toJson ["person", "act"]), ("description", .str "regulated"),
      ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "deny"),
        ("act", .str "{0} do y to {1}")])])]),
  ("constants", Json.mkObj [])]

/-- A one-unit document over `vocabulary` with `profiles`, its one unit `⊤`. -/
def text (profiles : List String) : String :=
  let environment := Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", vocabulary)]
  let unit := Json.mkObj [("id", .str "u1"), ("span", toJson [0, 9]), ("kind", .str "asserted"),
    ("meaning", .str "specified"), ("support", .str "assumption"), ("content", Json.mkObj [("ast", toJson ["top"])])]
  let front := Json.mkObj [("format", .str "ve-document@1"), ("environment", environment), ("units", toJson [unit]),
    ("open_terms", toJson ([] : List Json))]
  "---\n" ++ front.compress ++ "\n---\nUnit u1.\n"

def judged : List String := ["definitions@0", "documents@1", "judgments@0", "norms@0", "relational-fol@0"]

/-- The answer's member `key`, or the error. -/
def member (profiles : List String) (key : String) : Except String Json := do
  let row ← checkCore (Json.mkObj [("id", .str "d"), ("document", .str (text profiles)), ("admit", .bool false)])
  match row.getObjVal? key with
  | .ok v => pure v
  | .error _ => throw s!"no {key}: {row.compress}"

-- Spec 11.7 on the wire, in Lean's order: `due_date` has the word in another sense, `arrest` matches no row,
-- `reasonable_detention` is W3-defined; `trial` matches through its template; the regulated predicate is kept (F3′).
#guard (member judged "undeclared_evaluative").toOption ==
  some (toJson ["arbitrary", "make_reasonable_efforts", "reasonable_grounds", "trial"])
-- Without the profile the answer has no such member.
#guard (member (judged.erase "judgments@0") "undeclared_evaluative").toOption == none
#guard (member (judged.erase "judgments@0") "units").toOption.isSome
-- The base predicates as `undeclaredEvaluative` reads them: every one but the W3-defined name, each with its words.
#guard (do
    let E ← environmentOf (Json.parse ((text judged).drop 4 |>.takeWhile (· != '\n')) |>.toOption.getD .null
      |>.getObjValD "environment") (toJson ([] : List Json)) false
    pure E.basePredicates).toOption ==
  some [("arbitrary", ["arbitrary"]), ("arrest", ["arrest"]), ("due_date", ["due", "date"]),
    ("make_reasonable_efforts", ["make", "reasonable", "efforts"]), ("reasonable_grounds", ["reasonable", "grounds"]),
    ("trial", ["trial", "0", "is", "a", "fair", "trial"])]

end VE.Service.UndeclaredExamples
