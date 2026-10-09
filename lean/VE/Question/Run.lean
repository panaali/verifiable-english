import VE.Question.Texts
import VE.EnglishGrammar.Run

/-! The `english.question` service mode (docs/spec/question-answering.md 4.1 and 8; plan 4.8, Q1.2).

A case is `english.read`'s case (`id`, `environment`, `lexicon`, `overlay`?, `generated`?, `source`, `mode`, `cap`)
plus `question`. It is decoded by `VE.EnglishGrammar.Run.decodeCase`, imported and not copied. The source must be
the question, read in authoring mode at cap 2, so the six identities of E2 (`source_sha256` over the question) are
the ones `english.read` would give for the same request; `question_version` is added.

The result is `readQuestion`'s outcome under `auxiliaries` and E2's `workBudget`, with the fields of 4.1's row for
that outcome. Every span is in code points of the question. A case that cannot be read is an `error` row.
`one` also carries `text`, the A0 line of 3.3, so the CLI prints only Lean's words.

A case `{"id", "export": "codes"}` answers the question contract: the version, the codes with their classes,
the codes of every status and the fields of every status, so the relay holds no table of its own
(`tools/question_codes.py` writes it to `ve/question/codes.json`).
-/

namespace VE.Question.Run
open Lean VE.EnglishGrammar VE.EnglishGrammar.Run VE.Question

/-- The identity of the question contract. -/
def questionVersion : String := s!"question@{question_version}"

/-- Every code a question answer may carry with its class: the new question codes, then E2's. -/
def codeClasses : List (String × String) := newCodeClasses ++ VE.EnglishGrammar.Run.codeClasses

/-- The codes each status may carry (4.1). -/
def statusCodes : List (String × List String) :=
  [("notQuestion", ["NotOneQuestion"]),
   ("none", ["QuestionForm", "NoDerivation"]),
   ("budget", ["QuestionTooLong", "Budget"]),
   ("many", ["Ambiguous", "AmbiguousQuestion"]),
   ("indefinite", ["IndefiniteQuestion"]),
   ("rejected", rejectCodes ++ ["QuestionWithMarker", "IllTyped"]),
   ("invalidGrammar", ["InvalidGrammar", "InvalidOverlay"])]

/-- The fields each status carries besides `status` and `identities` (4.1, 8): required, then optional. -/
def statusFields : List (String × List String × List String) :=
  [("one", ["text", "form", "sentence", "ast", "spans"], []),
   ("many", ["code", "class", "text", "span"], ["rephrasings", "witnesses"]),
   ("indefinite", ["code", "class", "text", "span", "rephrasings"], []),
   ("none", ["code", "class", "text", "span"], ["advice"]),
   ("rejected", ["code", "class", "text", "span"], []),
   ("notQuestion", ["code", "class", "text", "span"], []),
   ("budget", ["code", "class", "text", "span"], []),
   ("invalidGrammar", ["code", "class", "text"], ["fault", "failure"])]

theorem statusCodes_classed : ∀ s ∈ statusCodes, ∀ c ∈ s.2, (codeClasses.lookup c).isSome = true := by
  decide

def coded (code text : String) : List (String × Json) :=
  [("code", .str code), ("text", .str text)] ++
    (codeClasses.lookup code |>.toList.map fun cls => ("class", Json.str cls))

/-- E2's text of a sentence-0 refusal, said of the question. -/
def ofQuestion (text : String) : String := text.replace "Sentence 1 " "The question "

/-- A byte span of the question in code points. -/
def pointSpan (q : String) (span : Nat × Nat) : Json :=
  spanJson (codepointsBefore q span.1, codepointsBefore q span.2)

def whole (q : String) : List (String × Json) := [("span", spanJson (0, q.length))]

def formName : Form → String
  | .caseThat => "caseThat"
  | .fronted .. => "fronted"

/-- Row 5: the body's lexing refused, its offset moved onto the question. A space before the `?` is the added
period's spacing, so it gets the question's own text. -/
def lexicalFields (q : String) (body : Nat) (r : Reject) : List (String × Json) :=
  let r' := shiftReject body r
  let text := match r with
    | .badSpacing o => if o + body + 1 == q.utf8ByteSize then badQuestionSpacingText (o + body)
        else ofQuestion (rejectText 0 r')
    | _ => ofQuestion (rejectText 0 r')
  status "rejected" ++ coded r.code text ++ ((lexicalSpan q r').map fun s => [("span", spanJson s)]).getD (whole q)

/-- Row 13: the first refused candidate's refusal. The other outcomes of `read` do not reach here (`got`). -/
def refusedFields (q : String) (E : Env) (L : Lexicon) (c : Candidate) : ReadOutcome →
    Except String (List (String × Json))
  | .ok _ => pure (status "rejected" ++ coded "QuestionWithMarker" markerText ++ whole q)
  | .illTyped => pure (status "rejected" ++ coded "IllTyped" illTypedQuestionText ++ whole q)
  | .stopped _ (.rejected r) =>
    pure (status "rejected" ++ coded r.code (ofQuestion (rejectionText c.sentence 0 r)) ++ whole q)
  | .invalidGrammar g =>
    pure (invalidFields "english.question" ⟨E, {}, L, none, []⟩ g)
  | _ => throw "InvalidInput: a refused candidate has no refusal"

/-- Row 10: E2's two witness trees of the candidate with two derivations. -/
def ambiguousFields (q : String) (E : Env) (L : Lexicon) (c : Candidate) : Except String (List (String × Json)) :=
  let tags := (grammar E L).rules.map (·.tag)
  match read E {} L workBudget c.sentence with
  | .stopped _ (.ambiguous t u) =>
    pure (status "many" ++ coded "Ambiguous"
      s!"The sentence \"{c.sentence}\" can be read in more than one way. Two of the ways are shown." ++
      whole q ++ [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
  | _ => throw "InvalidInput: an ambiguous candidate has no two derivations"

/-- Row 15's advice: the indefinite article's, else E2's advice row for the closest candidate's tokens. -/
def noneAdvice (profiles : List String) (q : String) (cl : Option Candidate) : List (String × Json) :=
  let row := match indefiniteSwaps auxiliaries q with
    | some (art, _, _) => some ("question-indefinite", s!"Write \"every\" or \"some\" in place of \"{art}\".")
    | none => cl.bind fun c => match lex c.sentence with
      | .ok ss => advice profiles ((ss[0]?).getD #[]).toList
      | .error _ => none
  row.toList.map fun (name, tip) => ("advice", Json.mkObj [("id", .str name), ("text", .str tip)])

/-- Row 15: no reading, with the closest candidate's diagnosis mapped onto the question when it is found. -/
def noneFields (profiles : List String) (q : String) (E : Env) (L : Lexicon) (cl : Option Candidate) :
    List (String × Json) :=
  let found := cl.bind fun c => (diagnosisOf E L c).map (c, ·)
  let main := match found with
    | some (c, d) => status "none" ++ coded "NoDerivation" (noDerivationText ++ closestText c d) ++
        [("span", pointSpan q (mapSpan c caseFrame.utf8ByteSize d.span))]
    | none => status "none" ++ coded "NoDerivation" noDerivationText ++ whole q
  main ++ noneAdvice profiles q cl

/-- The fields of 4.1's row for an outcome. -/
def outcomeFields (profiles : List String) (q : String) (E : Env) (L : Lexicon) :
    Outcome → Except String (List (String × Json))
  | .one c φ => pure (status "one" ++ [("text", .str (askedText c)), ("form", .str (formName c.form)),
      ("sentence", .str c.sentence),
      ("ast", φ.encode), ("spans", Json.arr #[spanJson (0, q.length)])])
  | .meanings _ rs => pure (status "many" ++ coded "AmbiguousQuestion" ambiguousQuestionText ++ whole q ++
      [("rephrasings", toJson rs)])
  | .ambiguous c => ambiguousFields q E L c
  | .indefinite art rs => pure (status "indefinite" ++ coded "IndefiniteQuestion" (indefiniteText art) ++
      whole q ++ [("rephrasings", toJson rs)])
  | .none cl => pure (noneFields profiles q E L cl)
  | .refused c o => refusedFields q E L c o
  | .form wh => pure (status "none" ++ coded "QuestionForm" (if wh then whQuestionText else formText auxiliaries) ++
      whole q)
  | .text (.invalidGrammar g) => pure (invalidFields "english.question" ⟨E, {}, L, none, []⟩ g)
  | .text (.lexical r) => pure (lexicalFields q (shape auxiliaries q).offset r)
  | .text _ => throw "InvalidInput: the question's text outcome is neither its vocabulary nor its lexing"
  | .notQuestion => pure (status "notQuestion" ++ coded "NotOneQuestion" notOneQuestionText ++ whole q)
  | .limit => pure (status "budget" ++ coded "QuestionTooLong" questionTooLongText ++ whole q)
  | .budget _ => pure (status "budget" ++ coded "Budget" workBudgetText ++ whole q)

/-- The question contract's own table (`{"id", "export": "codes"}`). -/
def codesCase (id : String) : Json :=
  VE.Route.Wire.ok id [("result", Json.mkObj [("codes", toJson codeClasses), ("statuses", toJson statusCodes),
    ("fields", toJson statusFields),
    ("question_version", .str questionVersion)])]

def questionCase (j : Json) : Except String Json := do
  if (j.getObjVal? "export").isOk then
    VE.Bridge.exactFields j ["id", "export"]
    let id ← VE.Bridge.stringField j "id"
    unless (← VE.Bridge.stringField j "export") == "codes" do throw "InvalidInput: export is codes when present"
    return codesCase id
  VE.Bridge.exactFields j ((["id", "environment", "lexicon", "source", "mode", "cap", "question"] ++
    optionalFields j))
  let id ← VE.Bridge.stringField j "id"
  let q ← VE.Bridge.stringField j "question"
  unless (← VE.Bridge.stringField j "source") == q do throw "InvalidInput: the source is not the question"
  unless (← VE.Bridge.stringField j "mode") == "authoring" do throw "InvalidInput: a question is read in authoring mode"
  unless (← (← j.getObjVal? "cap").getNat?) == 2 do throw "InvalidInput: a question is read at cap 2"
  let c ← decodeCase j
  let identities := Json.mkObj ([("source_sha256", .str (VE.CertificateWire.sha256 q.toUTF8))] ++ c.identities ++
    [("question_version", .str questionVersion)])
  let fields ← match c.overlayFailure with
    | some f => pure (invalidOverlayFields "english.question" f)
    | none => outcomeFields c.E.profiles q c.E c.L (readQuestion auxiliaries c.E {} c.L workBudget q)
  pure (VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))])

def caseReported (j : Json) : Json :=
  match questionCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Question.Run
