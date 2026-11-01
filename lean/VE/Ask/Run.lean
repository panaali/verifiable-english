import VE.Ask.Render
import VE.Ask.PlainAnswer
import VE.Ask.ZeroAnswer
import VE.Question.Run

/-! The `ask` service mode (docs/spec/question-answering.md 4.2, 8; plan 4.8, Q2.2, Q2.3).

A case is `{"id", "document", "question", "lexicon", "case", "names"}`: the document's text, the question, the
lexicon of the English reader's producer for the document's environment, the readings case Python's relay built for
the question (its conclusion the question's formula), and the reading names. Lean reads the question in the
document's vocabulary (`VE.Question.ask`); any outcome but one reading is the result, with `english.question`'s
fields for that outcome. Otherwise Lean replays the case bound to the document (`replayAsk`), renders the answer
(`answerFor`, `render`) and returns its lines, rows, leads, unused sentences and unchecked names, all rendered from
Lean's values. A request Lean cannot answer is an `error` row with Lean's text. -/

namespace VE.Ask.Run
open Lean VE.Ask VE.Readings VE.Question.Run

def reasonName : Reason → String := reasonFrame

def sourceJson : Source → Json
  | .unit u => Json.mkObj [("kind", .str "unit"), ("unit", .str u)]
  | .rules p => Json.mkObj [("kind", .str "rules"), ("predicate", .str p)]
  | .definition n => Json.mkObj [("kind", .str "definition"), ("name", .str n)]
  | .background => Json.mkObj [("kind", .str "background")]
  | .pair r m => Json.mkObj [("kind", .str "pair"), ("required", .str r), ("permission", .str m)]
  | .fill r m => Json.mkObj [("kind", .str "fill"), ("required", .str r), ("permission", .str m)]

def readingsJson (rs : List (String × Nat)) : Json := Json.arr (rs.map fun (s, i) => Json.arr #[.str s, toJson i]).toArray

def lineJson (l : Line) : Json :=
  Json.mkObj [("frame", .str (gateName l.frame)), ("text", .str l.text),
    ("source", (l.source.map sourceJson).getD .null),
    ("quote", (l.quote.map fun (u, t) => Json.arr #[.str u, .str t]).getD .null),
    ("readings", readingsJson l.readings),
    ("witness", (l.witness.map choiceJson).getD .null),
    ("unchecked", .bool l.unchecked)]

def rowJson (v : View) (r : Row) : Json :=
  Json.mkObj [("choice", choiceJson r.choice), ("lead", .str (leadKey r.lead)),
    ("reason", (r.reason.map fun x => Json.str (reasonName x)).getD .null),
    ("cited", Json.arr ((v.key r).2.map sourceJson).toArray),
    ("gaps", VE.Readings.Wire.gapsJson (if r.query == .refuted then v.gaps r.choice else []))]

def nameJson (n : Name) : Json := Json.mkObj [("set", .str n.set), ("index", toJson n.index), ("text", .str n.text)]

/-- The uniform lead, or `by_reading` when the answer has two or more blocks. -/
def answerLead (v : View) : String :=
  match v.groups with
  | [g] => leadKey g.lead
  | _ => "by_reading"

/-- The route a document is answered on, by its profiles: `readings@1` the readings route (RD-3), `norms@0` or
    `norm-defaults@0` the norm-defaults route, otherwise the plain adapter. -/
def routeOfDocument (text : String) : String :=
  match VE.Service.Document.split text with
  | .ok sp =>
    let ps := VE.Service.Document.listedProfiles (sp.front.getObjValD "environment")
    if ps.contains "readings@1" then "readings"
    else if ps.contains "norms@0" || ps.contains "norm-defaults@0" then "norm-defaults"
    else "plain"
  | .error _ => "plain"

/-- The answered result's fields, rendered from Lean's answer. -/
def answeredFields (route q : String) (c : VE.Question.Candidate) (φ : VE.EnglishGrammar.EFormula) (ctx : Context)
    (v : View) : List (String × Json) :=
  let lines := renderV ctx v
  [("status", .str "answered"), ("route", .str route), ("form", .str (formName c.form)), ("sentence", .str c.sentence),
   ("ast", φ.encode), ("spans", Json.arr #[VE.EnglishGrammar.Run.spanJson (0, q.length)]),
   ("lead", .str (answerLead v)),
   ("text", toJson (lines.map (·.text))),
   ("lines", Json.arr (lines.map lineJson).toArray),
   ("rows", Json.arr (v.rows.map (rowJson v)).toArray),
   ("unused", toJson v.unused),
   ("unchecked_names", Json.arr ((v.names.filter (!·.checked)).map nameJson).toArray)]

/-- RD-3's refusal past 64 compatible choices (`replayVerdictsND`). -/
def overChoices : String := "readings-verdicts: more than 64 compatible readings"

/-- X5 (spec 4.2 step 4): past 64 compatible choices RD-3 checks no row, so the answer is VE's limit, in X5's words
    (`ResourceLimit`, never a lead); RD-3's other refusals are relayed as they are. -/
def replayError (e : String) : String :=
  if e == overChoices then s!"ResourceLimit: {reasonText .tooMany}" else e

#guard replayError overChoices ==
  "ResourceLimit: There are more than 64 ways to read this document's open sentences. VE did not check them all."
#guard replayError "InvalidInput: the case does not ask this question" ==
  "InvalidInput: the case does not ask this question"

/-- The answer of a question read with one meaning, on the document's route. -/
def answered (route : String) (j : Json) (q : String) (c : VE.Question.Candidate) (φ : VE.EnglishGrammar.EFormula) :
    Except String (List (String × Json)) := do
  if route == "readings" then
    let s ← (replayAsk j).mapError replayError
    let (ctx, a) ← answerFor s
    pure (answeredFields route q c φ ctx a.view)
  else if route == "plain" then
    let s ← replayPlainAsk j
    let (ctx, _, v) ← answerForPlain s
    pure (answeredFields route q c φ ctx v)
  else
    let s ← replayZeroAsk j
    let (ctx, _, v) ← answerForZero s
    pure (answeredFields route q c φ ctx v)

/-- The identities of the answer: E2's (`source_sha256` over the question), the question contract's version, and
    the document's identity. -/
def identitiesOf (text q : String) (lexicon : Json) (E : VE.EnglishGrammar.Env) : Except String Json := do
  let sp ← VE.Service.Document.split text
  let environment := sp.front.getObjValD "environment"
  pure (Json.mkObj [("source_sha256", .str (VE.CertificateWire.sha256 q.toUTF8)),
    ("environment_id", .str (← VE.EnglishGrammar.Run.environmentId environment)),
    ("lexicon_id", .str (← VE.CertificateWire.digest "ve-english-lexicon-v1\n" lexicon)),
    ("grammar_id", .str (← VE.EnglishGrammar.Run.grammarId E.profiles)),
    ("actions_version", .str VE.EnglishGrammar.Fixed.actionsVersion),
    ("question_version", .str questionVersion),
    ("document_id", .str (← VE.Service.Document.documentId sp))])

/-- A string field of a field list, `""` otherwise. -/
def fieldText (fs : List (String × Json)) (k : String) : String :=
  match fs.lookup k with
  | some (.str t) => t
  | _ => ""

/-- A question VE does not read with one meaning: `english.question`'s status, code, class and text for it (its
    span, advice, rephrasings and witnesses are `english.question`'s, which the relay asks first). -/
def refusedFields (fs : List (String × Json)) : List (String × Json) :=
  [("status", .str (fieldText fs "status")), ("code", .str (fieldText fs "code")),
   ("class", .str (fieldText fs "class")), ("text", .str (fieldText fs "text"))]

def askCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ["id", "document", "question", "lexicon", "case", "names"]
  let id ← VE.Bridge.stringField j "id"
  let text ← VE.Bridge.stringField j "document"
  let q ← VE.Bridge.stringField j "question"
  let lexicon ← j.getObjVal? "lexicon"
  let (E, L) ← englishOf text lexicon
  let identities ← identitiesOf text q lexicon E
  match VE.Question.ask VE.Question.auxiliaries E {} L VE.EnglishGrammar.workBudget q with
  | .read (.one c φ) =>
    let fields ← answered (routeOfDocument text) j q c φ
    pure (VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))])
  | other =>
    let fields ← askedFields E.profiles q E L other
    pure (VE.Route.Wire.ok id [("result", Json.mkObj (refusedFields fields ++ [("identities", identities)]))])

def caseReported (j : Json) : Json :=
  match askCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Ask.Run
