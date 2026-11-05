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
    ("fair_detention", act.setObjVal! "defined" (Json.mkObj [("arguments", toJson ["act"]),
      ("body", toJson [toJson "unary", toJson "arrest", toJson [toJson "var", toJson 0]])])),
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
-- `reasonable_detention` and `fair_detention` are W3-defined; `trial` matches through its template; the regulated predicate is kept (F3′).
#guard (member judged "undeclared_evaluative").toOption ==
  some (toJson ["arbitrary", "make_reasonable_efforts", "reasonable_grounds", "trial"])
-- The usage map stays beside it.
#guard (member judged "judgments").toOption == some (Json.mkObj [("used", toJson ([] : List Json)),
  ("unused", toJson ([] : List Json))])
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

/-! ### jt-3b: authored fences and the report's lines

The bound names reach an authored fence through `contentOf`, and the report places jt-3's lines
(`tests/test_judgments_document.py` runs the same documents through `ve document check`). -/

def fenceVocabulary : Json := Json.mkObj [
  ("sorts", Json.mkObj [("limit", Json.mkObj [("description", .str "a limit")])]),
  ("constants", Json.mkObj [("atlas", Json.mkObj [("description", .str "a limit"), ("sort", .str "limit")])]),
  ("predicates", Json.mkObj (["reasonable_limit", "reasonable_grounds", "due_date", "published"].map fun p =>
    (p, Json.mkObj [("arguments", toJson ["limit"]), ("description", .str p)])))]

def plainProfiles : List String := ["documents@1", "relational-fol@0"]
def fenceProfiles : List String := ["documents@1", "judgments@0", "relational-fol@0"]

def pairs (rows : List (String × String)) : Json := Json.arr (rows.map fun (a, b) => toJson [a, b]).toArray

/-- The proposal Python sends for the environment the chain reads a fence in. -/
def lexicon : Json :=
  let env := Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson plainProfiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", fenceVocabulary)]
  Json.mkObj [("format", .str VE.EnglishGrammar.Run.lexiconFormat),
    ("environment_id", .str ((VE.EnglishGrammar.Run.environmentId env).toOption.getD "")),
    ("nouns", pairs [("limit", "limit")]), ("letters", pairs [("limit", "L")]),
    ("wordings", pairs [("due_date", "{0} is classified as \"due_date\""), ("published", "{0} is published"),
      ("reasonable_grounds", "{0} is classified as \"reasonable_grounds\""),
      ("reasonable_limit", "{0} is classified as \"reasonable_limit\"")]),
    ("negatives", toJson ([] : List String)), ("aliases", toJson ([] : List String)),
    ("spellings", pairs [("atlas", "atlas")])]

def term (name : String) (decider : String := "unstated") (factors : List String := []) : Json :=
  Json.mkObj [("name", .str name), ("arguments", toJson ["limit"]), ("decided_by", .str decider),
    ("necessary", toJson ([] : List String)), ("sufficient", toJson ([] : List String)), ("factors", toJson factors),
    ("precedents", toJson ([] : List String)), ("jurisdiction", .str "document"), ("version", toJson (1 : Nat))]

def opened (names : List String) : Json := Json.mkObj [("open", toJson names)]

/-- A one-unit document over a fence reading `sentence`. -/
def fenced (profiles : List String) (sentence : String) (terms : List Json := [])
    (meaning : Json := .str "specified") : String :=
  let environment := Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", fenceVocabulary)]
  let unit := Json.mkObj [("id", .str "a"), ("span", toJson [0, 14]), ("kind", .str "asserted"),
    ("meaning", meaning), ("support", .str "assumption"), ("content", Json.mkObj [("fence", .str "a")]),
    ("surface", .str "english")]
  let front := Json.mkObj [("format", .str "ve-document@1"), ("environment", environment), ("units", toJson [unit]),
    ("open_terms", toJson terms)]
  "---\n" ++ front.compress ++ "\n---\nAtlas is odd.\n```ve a\n" ++ sentence ++ "\n```\n"

def answer (text : String) : Except String Json :=
  checkCore (Json.mkObj [("id", .str "d"), ("document", .str text), ("admit", .bool false), ("lexicon", lexicon)])

def said (p : String) : String := s!"Atlas is classified as \"{p}\"."
def bound : String := fenced fenceProfiles (said "reasonable_limit")
  [term "reasonable_limit" "governance_function" ["the budget"]] (opened ["reasonable_limit"])
def refusal : String := "UndeclaredEvaluative: 'Reasonable' is a judgment. Say who decides it ('… is a judgment for " ++
  "the operator'), or define it ('In this document, a reasonable limit means …')."
def refused (text : String) : Option String := match answer text with
  | .error m => some m
  | .ok _ => none
def lines (text : String) : Option Json := ((answer text).toOption).bind (·.getObjVal? "judgment_lines" |>.toOption)

-- An unbound word in an authored fence is refused with 9.5's text, and only under the profile (J-λ).
#guard refused (fenced fenceProfiles (said "reasonable_limit")) == some refusal
#guard refused (fenced plainProfiles (said "reasonable_limit")) == none
-- Per predicate (DRI item 3): `reasonable_grounds` bound does not bind `reasonable_limit`, and binds itself.
#guard refused (fenced fenceProfiles (said "reasonable_limit") [term "reasonable_grounds"]) == some refusal
#guard refused (fenced fenceProfiles (said "reasonable_grounds") [term "reasonable_grounds"]
  (opened ["reasonable_grounds"])) == none
-- Bound, a plain word, and another sense (`due_date`) answer.
#guard refused bound == none
#guard refused (fenced fenceProfiles "Atlas is published.") == none
#guard refused (fenced fenceProfiles (said "due_date")) == none
-- Another refusal keeps its class, under the profile and without it.
#guard ((refused (fenced fenceProfiles "Atlas is odd.")).map (·.startsWith "SyntaxError: ")) == some true
#guard refused (fenced fenceProfiles "Atlas is odd.") == refused (fenced plainProfiles "Atlas is odd.")
-- The lines: the legend with the decider and the factors, the unit's neutral status line.
def boundLines : Json := Json.mkObj [
  ("legend", toJson [Json.mkObj [("term", .str "reasonable_limit"), ("lines", toJson [
    "Whether a limit is classified as \"reasonable_limit\" is a judgment for the governance function.",
    "The text mentions these points: the budget."])]]),
  ("status", toJson [Json.mkObj [("unit", .str "a"), ("line", .str
    "Open: this uses the judgment whether a limit is classified as \"reasonable_limit\".")]])]
#guard lines bound == some boundLines
-- An unused bound term has its legend and no status row; no line says who decides what the text leaves unstated.
#guard lines (fenced fenceProfiles "Atlas is published." [term "reasonable_grounds"]) == some (Json.mkObj [
  ("legend", toJson [Json.mkObj [("term", .str "reasonable_grounds"), ("lines", toJson [
    "Whether a limit is classified as \"reasonable_grounds\" is a judgment; the text does not say who makes it."])]]),
  ("status", toJson ([] : List Json))])
#guard lines (fenced plainProfiles "Atlas is published.") == none
-- Every term has its row, the third argument's factors included, in declaration order.
#guard legendRows [⟨"b", ["limit"], "unstated", ["f"]⟩, ⟨"a", ["limit", "limit"], "reviewer", []⟩] ==
  [("b", ["Whether a limit is classified as \"b\" is a judgment; the text does not say who makes it.",
      "The text mentions these points: f."]),
   ("a", ["Whether a limit has the recorded relation \"a\" to a limit (the same or another) is a judgment for the reviewer."])]
-- A soft document's `E″` keeps the names (`softContentOf` reads its fences over it); `tests/test_judgments_document.py`
-- runs a soft document's fence through the service.
#guard (do
    let E ← environmentOf ((Json.parse ((bound.drop 4).takeWhile (· != '\n'))).toOption.getD .null |>.getObjValD "environment")
      (toJson ([] : List Json)) false
    let X ← layeredIds { E with boundNames := some (toJson ["p"]) } E
    pure X.boundNames).toOption == some (some (toJson ["p"]))
-- Two judgments of one unit, in declaration order, and the rows of the units that depend on them.
def view (id : String) (ps : List String) : VE.Judgments.UnitView :=
  { id, meaning := "open", listed := ps, asserted := true, set := none,
    own := some (.formula (ps.foldr (fun p f => .and (.unary p (.var 0)) f) .top)) }
def declared : List VE.Judgments.Judgment := [⟨"a", ["limit"], "unstated", []⟩, ⟨"b", ["limit"], "unstated", []⟩]
#guard statusRows [] declared [view "u1" ["b", "a"], view "u2" [], view "u3" ["b"]] ==
  [("u1", "Open: this uses the judgments whether a limit is classified as \"a\" and whether a limit is classified as \"b\"."),
   ("u3", "Open: this uses the judgment whether a limit is classified as \"b\".")]

end VE.Service.UndeclaredExamples
