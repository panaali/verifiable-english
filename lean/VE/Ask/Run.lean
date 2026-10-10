import VE.Ask.Render
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

def rowJson (a : Answer) (r : Row) : Json :=
  Json.mkObj [("choice", choiceJson r.choice), ("lead", .str (leadKey r.lead)),
    ("reason", (r.reason.map fun x => Json.str (reasonName x)).getD .null),
    ("cited", Json.arr ((a.key r).2.map sourceJson).toArray)]

def nameJson (n : Name) : Json := Json.mkObj [("set", .str n.set), ("index", toJson n.index), ("text", .str n.text)]

/-- The uniform lead, or `by_reading` when the answer has two or more blocks. -/
def answerLead (a : Answer) : String :=
  match a.groups with
  | [g] => leadKey g.lead
  | _ => "by_reading"

/-- The answered result's fields, rendered from Lean's answer. -/
def answeredFields (q : String) (c : VE.Question.Candidate) (φ : VE.EnglishGrammar.EFormula) (ctx : Context)
    (a : Answer) : List (String × Json) :=
  let lines := render ctx a
  [("status", .str "answered"), ("form", .str (formName c.form)), ("sentence", .str c.sentence), ("ast", φ.encode),
   ("spans", Json.arr #[VE.EnglishGrammar.Run.spanJson (0, q.length)]),
   ("lead", .str (answerLead a)),
   ("text", toJson (lines.map (·.text))),
   ("lines", Json.arr (lines.map lineJson).toArray),
   ("rows", Json.arr (a.rows.map (rowJson a)).toArray),
   ("unused", toJson a.unused),
   ("unchecked_names", Json.arr ((a.names.filter (!·.checked)).map nameJson).toArray)]

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
    let s ← replayAsk j
    let (ctx, a) ← answerFor s
    pure (VE.Route.Wire.ok id [("result", Json.mkObj (answeredFields q c φ ctx a ++ [("identities", identities)]))])
  | other =>
    let fields ← askedFields E.profiles q E L other
    pure (VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))])

def caseReported (j : Json) : Json :=
  match askCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Ask.Run
