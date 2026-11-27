import VE.EnglishGrammar.Run
import VE.Question.Run

/-! 9.5's refusal through `english.read` (`Run.readCase`; DRI 2026-11-02, jt-3 item 1): only a request in authoring that
sends `judgments` can be refused, and translation answers the same with or without the field. The field is
`english.read`'s alone: the modes that share `optionalFields` refuse it (jt-3 review F1). -/

namespace VE.EnglishGrammar.JudgmentRunExamples
open Lean VE.EnglishGrammar.Run

def preds : List String := ["reasonable_limit", "published"]

def environment : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ["relational-fol@0"]),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [
      ("constants", Json.mkObj [("atlas", Json.mkObj [("description", .str "a limit"), ("sort", .str "limit")])]),
      ("predicates", Json.mkObj (preds.map fun p =>
        (p, Json.mkObj [("arguments", toJson ["limit"]), ("description", .str p)]))),
      ("sorts", Json.mkObj [("limit", Json.mkObj [("description", .str "a limit")])])])]

def pairs (rows : List (String × String)) : Json := Json.arr (rows.map fun (a, b) => toJson [a, b]).toArray

def lexicon : Json :=
  Json.mkObj [("format", .str lexiconFormat), ("environment_id", .str ((environmentId environment).toOption.getD "")),
    ("nouns", pairs [("limit", "limit")]), ("letters", pairs [("limit", "L")]),
    ("wordings", pairs [("published", "{0} is published"), ("reasonable_limit", "{0} is classified as \"reasonable_limit\"")]),
    ("negatives", toJson ([] : List String)), ("aliases", toJson ([] : List String)),
    ("spellings", pairs [("atlas", "atlas")])]

def plain : String := "Atlas is published."
def word : String := "Atlas is classified as \"reasonable_limit\"."

def request (source mode : String) (fields : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", .str "c"), ("environment", environment), ("lexicon", lexicon), ("source", .str source),
    ("mode", .str mode), ("cap", toJson (2 : Nat))] ++ fields)

def J (names : List String) : List (String × Json) := [("judgments", toJson names)]

def result (j : Json) : Json := ((readCase j).toOption.getD .null).getObjValD "result"
def member (j : Json) (key : String) : Json := (result j).getObjValD key

-- Refused with its text and sentence, the second here: every sentence of the reading is looked at.
#guard member (request (plain ++ " " ++ word) "authoring" (J [])) "status" == .str "rejected"
#guard member (request (plain ++ " " ++ word) "authoring" (J [])) "code" == .str "UndeclaredEvaluative"
#guard member (request (plain ++ " " ++ word) "authoring" (J [])) "sentence" == toJson (1 : Nat)
#guard member (request (word ++ " " ++ plain) "authoring" (J [])) "sentence" == toJson (0 : Nat)
#guard member (request (plain ++ " " ++ word) "authoring" (J [])) "class" == .str "SyntaxError"
#guard member (request word "authoring" (J [])) "text" == .str ("'Reasonable' is a judgment. Say who decides it " ++
  "('… is a judgment for the operator'), or define it ('In this document, a reasonable limit means …').")
-- Not refused: bound, without the field, or a sentence with no such word.
#guard member (request word "authoring" (J ["reasonable_limit"])) "status" == .str "one"
#guard member (request word "authoring") "status" == .str "one"
#guard member (request plain "authoring" (J [])) "status" == .str "one"
-- The three optional fields together; a malformed or over-long list is refused, in both modes.
#guard member (request word "authoring" ([("overlay", Json.mkObj []), ("generated", .bool true)] ++ J ["reasonable_limit"]))
  "status" == .str "one"
#guard (readCase (request word "authoring" [("judgments", .str "reasonable_limit")])).toOption.isNone
#guard (readCase (request word "translation" [("judgments", toJson [(7 : Nat)])])).toOption.isNone
def names (k : Nat) : List String := List.replicate k "n"
#guard member (request plain "authoring" (J (names JudgmentLines.maxJudgments))) "status" == .str "one"
#guard (readCase (request plain "authoring" (J (names (JudgmentLines.maxJudgments + 1))))).toOption.isNone
-- Translation answers the same, field or no field, byte for byte.
#guard [word, plain].all fun s => [[], ["reasonable_limit"], ["absent"]].all fun js =>
  ((readCase (request s "translation" (J js))).toOption.map (·.compress)) ==
    ((readCase (request s "translation")).toOption.map (·.compress))

-- `judgments` is `english.read`'s alone: `english.grammar`, `english.check` and `english.question` share
-- `optionalFields` with it and refuse the field, as on the merge base, rather than drop the opt-in unread.
def question : String := "Is Atlas published?"
def shared (fields : List (String × Json)) : List (Except String Json) :=
  let g := [("environment", environment), ("lexicon", lexicon)] ++ fields
  let empty : Json := toJson ([] : List Json)
  [grammarCase (Json.mkObj ([("id", .str "g")] ++ g)),
   checkCase (Json.mkObj ([("id", .str "k"), ("formulas", empty), ("marks", empty), ("candidates", empty)] ++ g)),
   VE.Question.Run.questionCase (request question "authoring" ([("question", .str question)] ++ fields))]
def mismatch : Except String Json → Bool
  | .error m => m.startsWith "fields do not match: expected " &&
    ((m.splitOn "got").head!.splitOn "judgments").length == 1
  | .ok _ => false
#guard (shared []).all (·.toOption.isSome)
#guard (shared [("overlay", Json.mkObj [])]).all (·.toOption.isSome)
#guard [J [], J ["reasonable_limit"], [("judgments", .str "x")]].all fun f => (shared f).all mismatch
#guard (shared ([("overlay", Json.mkObj [])] ++ J [])).all mismatch

-- `sentence_base` (row plain-vocab-refusal-number-1126): the sentences before the source, a document fence's index
-- (`Service.Document.contentOf`). Every refusal text counts from it; `sentence` and the spans stay the source's own.
-- Absent it is 0; a value that is not a natural number is refused; it is `english.read`'s alone. Authoring mode reads it;
-- translation mode (one sentence, never a document fence) validates it and numbers from 1 as before.
#guard ((member (request "Atlas is odd." "authoring" [("sentence_base", toJson (1 : Nat))]) "text").getStr?.toOption.getD
  "").startsWith "Sentence 2 has no reading with the current vocabulary."
#guard member (request "Atlas is odd." "authoring" [("sentence_base", toJson (1 : Nat))]) "sentence" == toJson (0 : Nat)
#guard ((member (request (plain ++ " Atlas is odd.") "authoring" [("sentence_base", toJson (2 : Nat))]) "text").getStr?
  |>.toOption.getD "").startsWith "Sentence 4 has no reading"
#guard member (request "." "authoring" [("sentence_base", toJson (1 : Nat))]) "text" == .str "Sentence 2 is empty."
#guard member (request plain "authoring" [("sentence_base", toJson (3 : Nat))]) "status" == .str "one"
#guard ["Atlas is odd.", plain, "."].all fun s =>
  ((readCase (request s "authoring" [("sentence_base", toJson (0 : Nat))])).toOption.map (·.compress)) ==
    ((readCase (request s "authoring")).toOption.map (·.compress))
#guard [Json.str "1", toJson (-1 : Int), .bool true, toJson [(1 : Nat)]].all fun v =>
  match readCase (request plain "authoring" [("sentence_base", v)]) with
  | .error m => m == "InvalidInput: sentence_base is a natural number"
  | .ok _ => false
#guard (shared [("sentence_base", toJson (1 : Nat))]).all mismatch
-- `Budget` (a budget-tripping read is not cheap, so the text is checked on `budgetFields` itself).
#guard VE.Bridge.lookup (budgetFields 0 (base := 1)) "text" ==
  some (.str "Sentence 2 needs more work than the limit allows. No verdict was reached.")
#guard VE.Bridge.lookup (budgetFields 0 (base := 1)) "sentence" == some (toJson (0 : Nat))
#guard budgetFields 2 == budgetFields 2 (base := 0)
-- With a base the premise texts say the premises are the fence's own (each fence is read alone); without, as before.
#guard noPremiseText 0 (base := 2) ==
  "Sentence 3 is marked as a conclusion, and no earlier sentence in its fence is a premise."
#guard noPremiseText 1 == "Sentence 2 is marked as a conclusion, and no earlier sentence is a premise."
#guard unprovedText 1 (base := 2) == "Sentence 4 is marked as a conclusion, and no checked derivation from the " ++
  "earlier premises in its fence was found: {status}"
#guard unprovedText 1 == unprovedText 1 (base := 0)
#guard ((member (request "Atlas is odd." "translation" [("sentence_base", toJson (3 : Nat))]) "text").getStr?
  |>.toOption.getD "").startsWith "Sentence 1 has no reading"

end VE.EnglishGrammar.JudgmentRunExamples
